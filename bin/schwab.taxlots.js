(function () {
    'use strict';

    const taxLotData = {};
    const processedButtons = new Set();
    let currentIndex = 0;
    let nextStepButtons = [];

    function log(message) {
        console.log('[Tax Lot Extractor]', message);
    }

    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    function parseValue(text) {
        if (!text) return 0;
        const cleanText = text.replace(/[$,\s+%]/g, '');
        return parseFloat(cleanText) || 0;
    }

    function parseDate(dateStr) {
        if (!dateStr) return '';
        return dateStr.trim();
    }

    function extractSymbolFromTitle(titleText) {
        const match = titleText.match(/Lot Details:\s*([A-Z\/]+)\s*-/);
        return match ? match[1] : null;
    }

    function extractLotDetailsFromTable() {
        const table = document.getElementById('responsiveLotTable');
        if (!table) {
            log('Lot details table not found');
            return null;
        }

        const rows = table.querySelectorAll('tbody tr.data-row');
        const lots = [];

        rows.forEach(row => {
            const openDateCell = row.querySelector('th span');
            const qtyCell = row.querySelector('td[name="Qty"]');
            const priceCell = row.querySelector('td[name="Price"]');
            const cpsCell = row.querySelector('td[name="CPS"] span');
            const mktValCell = row.querySelector('td[name="MktVal"] span');
            const costBasisCell = row.querySelector('td[name="CostBasis"] span');
            const gainLossCell = row.querySelector('td[name="GainLoss"] span');
            const gainLossPercentCell = row.querySelector('td[name="GainLossPercent"] span');
            const holdPeriodCell = row.querySelector('td[name="HoldPeriod"] span');

            if (openDateCell && qtyCell && priceCell) {
                lots.push({
                    open_date: parseDate(openDateCell.textContent),
                    quantity: parseValue(qtyCell.textContent),
                    price: parseValue(priceCell.textContent),
                    cost_per_share: parseValue(cpsCell?.textContent),
                    market_value: parseValue(mktValCell?.textContent),
                    cost_basis: parseValue(costBasisCell?.textContent),
                    gain_or_loss: parseValue(gainLossCell?.textContent),
                    gain_or_loss_percentage: parseValue(gainLossPercentCell?.textContent),
                    holding_period: holdPeriodCell?.textContent?.trim() || ''
                });
            }
        });

        return lots;
    }

    function getOpenLotModal() {
        const titleElement = document.getElementById('open-lot-overlay-modal-title');
        const modalOverlay = titleElement?.closest('.sdps-modal__overlay--open') ||
            document.querySelector('#open-lot-overlay .sdps-modal__overlay--open');
        if (modalOverlay) {
            return { container: modalOverlay, titleElement };
        }

        const modalHost = document.getElementById('open-lot-overlay');
        if (modalHost?.classList.contains('sdps-modal--open')) {
            return { container: modalHost, titleElement };
        }

        return null;
    }

    async function waitForLotDetailsModal(timeoutMs = 10000) {
        const deadline = Date.now() + timeoutMs;

        while (Date.now() < deadline) {
            const modal = getOpenLotModal();
            if (
                modal &&
                modal.titleElement &&
                document.getElementById('responsiveLotTable')
            ) {
                return modal;
            }
            await delay(250);
        }

        return getOpenLotModal();
    }

    async function processLotDetails(accountId, symbol) {
        const modal = await waitForLotDetailsModal();
        if (!modal) {
            log('Overlay not found or not open');
            return false;
        }

        const { container: overlay, titleElement } = modal;
        const extractedSymbol = extractSymbolFromTitle(titleElement.textContent);
        if (!extractedSymbol) {
            log('Could not extract symbol from title');
            return false;
        }

        if (extractedSymbol !== symbol) {
            log(`Symbol mismatch: expected ${symbol}, got ${extractedSymbol}`);
        }

        const lots = extractLotDetailsFromTable();
        if (!lots || lots.length === 0) {
            log('No lot details found');
            return false;
        }

        if (!taxLotData[accountId]) {
            taxLotData[accountId] = [];
        }

        let symbolObj = taxLotData[accountId].find(item => item[symbol]);
        if (!symbolObj) {
            symbolObj = {};
            symbolObj[symbol] = [];
            taxLotData[accountId].push(symbolObj);
        }

        symbolObj[symbol] = symbolObj[symbol].concat(lots);

        log(`Extracted ${lots.length} lots for ${symbol} in account ${accountId}`);

        const closeButton = overlay.querySelector('.sdps-modal__close');
        if (closeButton) {
            closeButton.click();
            await delay(1000);
        }

        return true;
    }

    async function clickLotDetails(button) {
        const row = button.closest('tr[data-symbol]');
        const symbol = row ? row.getAttribute('data-symbol') : 'unknown';

        const accountContainer = button.closest('tbody[id*="holdingsAccount_"]');
        const accountId = accountContainer ? accountContainer.id : 'holdingsAccount_unknown';
        const uniqueId = `${accountId}-${symbol}`;

        if (processedButtons.has(uniqueId)) {
            log(`Button for ${symbol} in account ${accountId} already processed, skipping`);
            return false;
        }

        log(`Clicking Next Steps button for: ${symbol} in account ${accountId}`);
        clickControl(button);
        const lotDetailsButton = await waitForLotDetailsOption();

        if (!lotDetailsButton) {
            log('Lot Details option not found');
            clickControl(button);
            await delay(500);
            return false;
        }

        log('Clicking Lot Details option');
        clickControl(lotDetailsButton);

        const success = await processLotDetails(accountId, symbol);
        processedButtons.add(uniqueId);
        return success;
    }

    function isVisible(element) {
        const rect = element.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return false;

        const style = window.getComputedStyle(element);
        return style.display !== 'none' &&
            style.visibility !== 'hidden' &&
            element.getAttribute('aria-hidden') !== 'true';
    }

    function isNextStepsControl(element) {
        const labels = [
            element.getAttribute('sdps-id'),
            element.getAttribute('sdps-name'),
            element.getAttribute('sdps-aria-label'),
            element.getAttribute('aria-label'),
            element.getAttribute('title'),
            element.textContent
        ]
            .filter(Boolean)
            .map(label => label.replace(/\s+/g, ' ').trim().toLowerCase());

        return labels.some(label =>
            label.includes('next steps') ||
            label.includes('next-steps')
        ) || Boolean(element.closest('app-next-steps-column'));
    }

    function findNextStepButtons() {
        const candidates = document.querySelectorAll(
            'sdps-button[sdps-id*="next-steps"], ' +
            'app-next-steps-column sdps-button, ' +
            'sdps-button, button, [role="button"], [sdps-name], [aria-label]'
        );
        const buttons = [];

        Array.from(candidates).forEach(candidate => {
            if (!isNextStepsControl(candidate) || !isVisible(candidate)) return;

            const duplicate = buttons.find(button =>
                button === candidate ||
                button.contains(candidate) ||
                candidate.contains(button)
            );
            if (!duplicate) buttons.push(candidate);
        });

        return buttons;
    }

    function clickControl(element) {
        const clickable = element.closest('button, [role="menuitem"], [role="option"]') || element;
        const nativeButton = clickable.matches('button') ? clickable : clickable.querySelector('button');
        (nativeButton || clickable).click();
    }

    function findLotDetailsOption() {
        const candidates = document.querySelectorAll(
            '#nextStepsList span, #nextStepsList button, ' +
            '[role="menuitem"], [role="option"], button, span, li, a'
        );

        return Array.from(candidates).find(candidate =>
            candidate.textContent.replace(/\s+/g, ' ').trim().toLowerCase() === 'lot details' &&
            isVisible(candidate)
        );
    }

    async function waitForLotDetailsOption(timeoutMs = 10000) {
        const deadline = Date.now() + timeoutMs;

        while (Date.now() < deadline) {
            const option = findLotDetailsOption();
            if (option) return option;
            await delay(250);
        }

        return findLotDetailsOption();
    }

    async function waitForNextStepButtons(timeoutMs = 20000) {
        const deadline = Date.now() + timeoutMs;

        while (Date.now() < deadline) {
            const buttons = findNextStepButtons();
            if (buttons.length > 0) return buttons;
            await delay(500);
        }

        return findNextStepButtons();
    }

    async function processNextButton() {
        if (currentIndex >= nextStepButtons.length) {
            log('All buttons processed');
            displayResults();
            return;
        }

        const button = nextStepButtons[currentIndex];
        log(`Processing button ${currentIndex + 1} of ${nextStepButtons.length}`);

        try {
            await clickLotDetails(button);
        } catch (error) {
            log(`Error processing button ${currentIndex}: ${error.message}`);
        }

        currentIndex++;
        setTimeout(processNextButton, 2000);
    }

    function escapeCSVField(field) {
        if (field === null || field === undefined) return '';

        const value = String(field);
        if (value.includes(',') || value.includes('"') || value.includes('\n')) {
            return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
    }

    function convertAccountToCSV(accountId, symbolArray) {
        const rows = [[
            'Account ID',
            'Symbol',
            'Open Date',
            'Quantity',
            'Price',
            'Cost Per Share',
            'Market Value',
            'Cost Basis',
            'Gain/Loss ($)',
            'Gain/Loss (%)',
            'Holding Period'
        ]];

        symbolArray.forEach(symbolObj => {
            Object.entries(symbolObj).forEach(([symbol, lots]) => {
                lots.forEach(lot => {
                    rows.push([
                        accountId,
                        symbol,
                        lot.open_date,
                        lot.quantity,
                        lot.price,
                        lot.cost_per_share,
                        lot.market_value,
                        lot.cost_basis,
                        lot.gain_or_loss,
                        lot.gain_or_loss_percentage,
                        lot.holding_period
                    ]);
                });
            });
        });

        return rows.map(row => row.map(escapeCSVField).join(',')).join('\n');
    }

    function accountFilename(accountId) {
        const accountLabel = accountId
            .replace(/^holdingsAccount_/i, 'account-')
            .replace(/[^a-z0-9_-]/gi, '-')
            .replace(/-+/g, '-')
            .replace(/^-|-$/g, '') || 'account-unknown';
        return `schwab-tax-lots-${accountLabel}.csv`;
    }

    function downloadCSV(filename, content) {
        const blob = new Blob([content], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    function displayResults() {
        log('=== EXTRACTION COMPLETE ===');
        console.log('Tax Lot Data:', JSON.stringify(taxLotData, null, 2));

        const accounts = Object.keys(taxLotData);
        let totalSymbols = 0;
        let totalPositions = 0;

        accounts.forEach(accountId => {
            const symbolArray = taxLotData[accountId];
            downloadCSV(accountFilename(accountId), convertAccountToCSV(accountId, symbolArray));

            symbolArray.forEach(symbolObj => {
                const symbols = Object.keys(symbolObj);
                totalSymbols += symbols.length;
                symbols.forEach(symbol => {
                    totalPositions += symbolObj[symbol].length;
                });
            });
        });

        alert(
            `Extraction complete! Found ${totalSymbols} symbols across ${accounts.length} accounts ` +
            `with ${totalPositions} total lot entries. Saved one CSV per account.`
        );
    }

    async function init() {
        log('Starting tax lot extraction...');

        if (!window.location.href.includes('client.schwab.com/app/accounts/positions')) {
            alert('Please navigate to https://client.schwab.com/app/accounts/positions/#/ first');
            return;
        }

        log('Waiting for the positions table to load...');
        nextStepButtons = await waitForNextStepButtons();
        log(`Found ${nextStepButtons.length} Next Steps buttons`);

        if (nextStepButtons.length === 0) {
            alert('No Next Steps buttons found. Make sure you are on the positions page.');
            return;
        }

        processNextButton();
    }

    init();
}());
