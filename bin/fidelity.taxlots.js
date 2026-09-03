(function () {
    'use strict';

    const accounts = new Map();
    const processedPositions = new Set();
    const usedFilenames = new Set();

    function log(message) {
        console.log('[Fidelity Tax Lot Extractor]', message);
    }

    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async function waitFor(predicate, timeoutMs = 10000, intervalMs = 100) {
        const deadline = Date.now() + timeoutMs;

        while (Date.now() < deadline) {
            const result = predicate();
            if (result) return result;
            await delay(intervalMs);
        }

        return predicate();
    }

    function cleanText(value) {
        return (value || '').replace(/\s+/g, ' ').trim();
    }

    function isVisible(element) {
        if (!element || element.hidden) return false;

        const style = window.getComputedStyle(element);
        return style.display !== 'none' &&
            style.visibility !== 'hidden' &&
            element.getAttribute('aria-hidden') !== 'true';
    }

    function getGrid() {
        return document.getElementById('posweb-grid');
    }

    function getGridRows() {
        const container = getGrid()?.querySelector('.ag-pinned-left-cols-container');
        if (!container) return [];

        return Array.from(container.children).filter(element =>
            element.matches('[role="row"]')
        );
    }

    function getAccountName(accountRow) {
        return cleanText(
            accountRow?.querySelector('.posweb-cell-account_primary')?.textContent
        ) || 'Account';
    }

    function getSymbol(positionRow) {
        const symbol = positionRow.querySelector(
            '.posweb-cell-symbol-name_container > span:first-child'
        );
        return cleanText(symbol?.textContent);
    }

    function getDescription(positionRow) {
        return cleanText(
            positionRow.querySelector('.posweb-cell-symbol-description')?.textContent
        );
    }

    function getPositionButton(positionRow) {
        return positionRow.querySelector(
            'button.posweb-cell-symbol-name'
        );
    }

    function getPositionEntries() {
        const rows = getGridRows();
        const entries = [];
        let currentAccount = null;

        rows.forEach(row => {
            if (row.classList.contains('posweb-row-account')) {
                currentAccount = {
                    key: row.getAttribute('row-id') || `account-${entries.length + 1}`,
                    name: getAccountName(row)
                };
                if (!accounts.has(currentAccount.key)) {
                    accounts.set(currentAccount.key, {
                        name: currentAccount.name,
                        lots: []
                    });
                }
                return;
            }

            const button = getPositionButton(row);
            if (
                !currentAccount ||
                !row.classList.contains('posweb-row-position') ||
                row.classList.contains('ag-full-width-row') ||
                !button
            ) {
                return;
            }

            const symbol = getSymbol(row);
            const rowId = row.getAttribute('row-id');
            if (!symbol || !rowId || symbol.toLowerCase() === 'cash') return;

            entries.push({
                rowId,
                accountKey: currentAccount.key,
                accountName: currentAccount.name,
                symbol,
                description: getDescription(row)
            });
        });

        return entries;
    }

    function findPositionRow(rowId) {
        return getGridRows().find(row => row.getAttribute('row-id') === rowId);
    }

    function findDrawer(rowId) {
        return Array.from(document.querySelectorAll(
            '#posweb-grid .ag-row.posweb-row-position.ag-full-width-row'
        )).find(row => row.getAttribute('row-id') === `detail_${rowId}`);
    }

    function drawerHasNoLotsMessage(drawer) {
        return Array.from(drawer.querySelectorAll(
            '.posweb-drawer-notification, .posweb-drawer-body'
        )).some(element =>
            isVisible(element) &&
            /\bno (?:tax )?lots?\b|\blots? (?:are )?not available\b/i.test(
                cleanText(element.textContent)
            )
        );
    }

    function drawerIsReady(drawer) {
        return Boolean(
            drawer &&
            (
                drawer.querySelector('.posweb-purchase-history') ||
                drawerHasNoLotsMessage(drawer)
            )
        );
    }

    function getPurchaseHistoryTab(drawer) {
        return drawer.querySelector(
            'button[aria-controls*="tabpanel-lots"], ' +
            'button[id^="posweb-header-purchase-history-tab-"]'
        );
    }

    function selectPurchaseHistoryTab(drawer) {
        const tab = getPurchaseHistoryTab(drawer);
        if (!tab) return false;

        if (tab.getAttribute('aria-selected') !== 'true') {
            tab.click();
        }
        return true;
    }

    async function openDrawer(entry) {
        let drawer = findDrawer(entry.rowId);
        if (!drawer) {
            const row = findPositionRow(entry.rowId);
            const button = getPositionButton(row);
            if (!button) {
                log(`Could not find the ${entry.symbol} row`);
                return null;
            }

            button.click();
        }

        drawer = await waitFor(() => findDrawer(entry.rowId));
        if (!drawer) return null;

        if (!selectPurchaseHistoryTab(drawer)) {
            log(`Purchase history tab not found for ${entry.symbol}`);
            return null;
        }

        return waitFor(() => {
            const currentDrawer = findDrawer(entry.rowId);
            return drawerIsReady(currentDrawer) ? currentDrawer : null;
        });
    }

    function getCellValues(row) {
        return Array.from(row.querySelectorAll('td')).map(cell =>
            cleanText(cell.textContent)
        );
    }

    function extractLots(drawer) {
        const table = drawer.querySelector('.posweb-purchase-history');
        if (!table) return [];

        return Array.from(table.querySelectorAll(
            'tbody tr.posweb-lots-table-row'
        )).map(row => {
            const cells = getCellValues(row);
            return {
                acquired: cells[0] || '',
                term: cells[1] || '',
                gain_loss: cells[2] || '',
                gain_loss_percent: cells[3] || '',
                current_value: cells[4] || '',
                quantity: cells[5] || '',
                average_cost_basis: cells[6] || '',
                cost_basis_total: cells[7] || ''
            };
        });
    }

    async function closeDrawer(drawer, rowId) {
        const closeButton = drawer.querySelector(
            'button[aria-label="Close Drawer"]'
        );
        if (!closeButton) return;

        closeButton.click();
        await waitFor(() => {
            const row = findPositionRow(rowId);
            return !findDrawer(rowId) ||
                getPositionButton(row)?.getAttribute('aria-expanded') !== 'true';
        }, 3000);
    }

    async function processPosition(entry) {
        const key = `${entry.accountKey}:${entry.rowId}`;
        if (processedPositions.has(key)) return;

        log(`Opening ${entry.symbol} in ${entry.accountName}`);
        const drawer = await openDrawer(entry);
        if (!drawer) {
            log(`Timed out loading ${entry.symbol} in ${entry.accountName}`);
            processedPositions.add(key);
            return;
        }

        const lots = extractLots(drawer);
        if (lots.length === 0) {
            log(`No tax lots found for ${entry.symbol} in ${entry.accountName}`);
        } else {
            const account = accounts.get(entry.accountKey);
            if (!account) {
                throw new Error(`Account not found for ${entry.symbol}`);
            }
            account.lots.push({
                symbol: entry.symbol,
                description: entry.description,
                lots
            });
            log(`Extracted ${lots.length} lots for ${entry.symbol} in ${entry.accountName}`);
        }

        await closeDrawer(drawer, entry.rowId);
        processedPositions.add(key);
    }

    function escapeCSVField(value) {
        const text = String(value ?? '');
        return /[",\n]/.test(text)
            ? `"${text.replace(/"/g, '""')}"`
            : text;
    }

    function accountFilename(accountName) {
        const label = accountName
            .replace(/[^a-z0-9_-]/gi, '-')
            .replace(/-+/g, '-')
            .replace(/^-|-$/g, '') || 'account';
        const base = `fidelity-tax-lots-${label}`;
        let filename = `${base}.csv`;
        let suffix = 2;

        while (usedFilenames.has(filename)) {
            filename = `${base}-${suffix}.csv`;
            suffix++;
        }
        usedFilenames.add(filename);
        return filename;
    }

    function accountCSV(account) {
        const rows = [[
            'Account Name',
            'Symbol',
            'Description',
            'Acquired',
            'Term',
            'Total Gain/Loss',
            'Total Gain/Loss (%)',
            'Current Value',
            'Quantity',
            'Average Cost Basis',
            'Cost Basis Total'
        ]];

        account.lots.forEach(position => {
            position.lots.forEach(lot => {
                rows.push([
                    account.name,
                    position.symbol,
                    position.description,
                    lot.acquired,
                    lot.term,
                    lot.gain_loss,
                    lot.gain_loss_percent,
                    lot.current_value,
                    lot.quantity,
                    lot.average_cost_basis,
                    lot.cost_basis_total
                ]);
            });
        });

        return rows.map(row => row.map(escapeCSVField).join(',')).join('\n');
    }

    function downloadCSV(filename, content) {
        const blob = new Blob([content], { type: 'text/csv;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    async function waitForPositionEntries(timeoutMs = 10000) {
        const deadline = Date.now() + timeoutMs;
        let lastSignature = '';
        let stableSince = 0;

        while (Date.now() < deadline) {
            const entries = getPositionEntries();
            if (entries.length > 0) {
                const signature = entries.map(entry => entry.rowId).join('|');
                if (signature !== lastSignature) {
                    lastSignature = signature;
                    stableSince = Date.now();
                } else if (Date.now() - stableSince >= 500) {
                    return entries;
                }
            }
            await delay(100);
        }

        return getPositionEntries();
    }

    async function exportAccounts() {
        let totalSymbols = 0;
        let totalLots = 0;
        let exportedAccounts = 0;

        for (const account of accounts.values()) {
            if (account.lots.length === 0) continue;

            downloadCSV(accountFilename(account.name), accountCSV(account));
            exportedAccounts++;
            totalSymbols += account.lots.length;
            totalLots += account.lots.reduce(
                (count, position) => count + position.lots.length,
                0
            );
            await delay(250);
        }

        alert(
            `Extraction complete! Found ${totalSymbols} symbols across ` +
            `${exportedAccounts} accounts with ${totalLots} total lot entries. ` +
            'Saved one CSV per account.'
        );
    }

    async function init() {
        log('Starting tax lot extraction...');

        const grid = await waitFor(getGrid, 10000);
        if (!grid) {
            alert('Please navigate to Fidelity\'s Positions page first.');
            return;
        }

        const entries = await waitForPositionEntries();
        if (!entries || entries.length === 0) {
            alert('No non-cash positions found on Fidelity\'s Positions page.');
            return;
        }

        log(`Found ${entries.length} non-cash positions`);
        for (const entry of entries) {
            await processPosition(entry);
        }

        await exportAccounts();
    }

    init().catch(error => {
        console.error('[Fidelity Tax Lot Extractor]', error);
        alert(`Fidelity tax lot extraction failed: ${error.message}`);
    });
}());
