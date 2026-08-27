/**
 * Bankrate Down-Payment NPV Scanner
 * -----------------------------------
 * Steps the "Down payment %" field on bankrate.com/mortgages/mortgage-rates/
 * from 20% to 35%, reads every qualifying lender's data (rate, monthly
 * payment, upfront costs, loan term), computes the NPV of total interest
 * paid over 8 years plus upfront costs at a configurable discount rate,
 * and ranks the top loans across the session.
 *
 * Results persist in memory across bookmarklet clicks and clear on page
 * reload. Displayed in a floating panel (no alert() used).
 *
 * IMPORTANT — read this:
 * Bankrate's rate table is a React app with auto-generated class names that
 * can change at any time and aren't visible from a plain HTML fetch. So
 * instead of hardcoded selectors, this script finds fields by their
 * *visible label text* and *value shape* (e.g. the down-payment % input is
 * assumed to hold the smaller of the two numbers in the "Down payment"
 * widget, since 20-35 is obviously smaller than a dollar amount).
 *
 * If it can't find something, it will log a clear error/warning telling you
 * what failed — open DevTools (F12) -> Console to see it, and adjust the
 * finder functions below if needed.
 */
(async function () {
  const CONFIG = {
    startPct: 20,
    endPct: 35,
    stepPct: 2,
    delayMs: 3500,
    discountRate: 7,     // annual %, opportunity cost of capital
    appreciationRate: 3,  // annual %, expected property appreciation
    projectionYears: 8,   // years to project equity and costs
    topN: 10,
  };

  const MIN_SCORE = 4.4;
  const projectionMonths = () => CONFIG.projectionYears * 12;

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  // Sets a value on a React-controlled <input> the way React expects
  // (via the native property setter) so React's onChange actually fires.
  function setNativeValue(el, value) {
    const proto =
      el.tagName === 'TEXTAREA'
        ? window.HTMLTextAreaElement.prototype
        : window.HTMLInputElement.prototype;
    const descriptor = Object.getOwnPropertyDescriptor(proto, 'value');
    descriptor.set.call(el, value);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }

  // Finds the "Down payment" widget's two inputs ($ amount and %).
  // Returns { percentInput, dollarInput } (either may be null).
  function findDownPaymentInputs() {
    const allEls = Array.from(document.querySelectorAll('body *'));
    const labelEl = allEls.find(
      (el) => el.children.length === 0 && /down payment/i.test(el.textContent || '')
    );
    if (!labelEl) return { percentInput: null, dollarInput: null };

    let container = labelEl.closest('div');
    for (let hop = 0; hop < 6 && container; hop++) {
      const inputs = Array.from(container.querySelectorAll('input'));
      if (inputs.length >= 2) {
        const withVals = inputs.map((inp) => ({
          inp,
          val: parseFloat((inp.value || '').replace(/[^0-9.]/g, '')) || 0,
        }));
        withVals.sort((a, b) => a.val - b.val);
        // Smallest number = the percent field (20-35), largest = the $ field.
        return {
          percentInput: withVals[0].inp,
          dollarInput: withVals[withVals.length - 1].inp,
        };
      }
      container = container.parentElement;
    }
    return { percentInput: null, dollarInput: null };
  }

  // Some filter changes on Bankrate require clicking "Update" to refresh
  // the table. Click it if present; harmless no-op if not.
  function findUpdateButton() {
    const els = Array.from(document.querySelectorAll('button, a'));
    return els.find((el) => /^update$/i.test((el.textContent || '').trim()));
  }

  // Reads every lender <article>, skips those with customer score < MIN_SCORE,
  // and returns full loan data for qualifying lenders.
  function collectLenderData() {
    const articles = Array.from(document.querySelectorAll('article'));
    const lenders = [];
    for (const art of articles) {
      const scoreEl =
        art.querySelector('[data-testid="customer-score-desktop"]') ||
        art.querySelector('[data-testid="customer-score-mobile"]');
      if (scoreEl) {
        const score = parseFloat((scoreEl.textContent || '').replace(/[^0-9.]/g, ''));
        if (!isNaN(score) && score < MIN_SCORE) continue;
      }

      const nameEl = art.querySelector('.font-bold') || art.querySelector('.font-normal');
      const lenderName = nameEl ? nameEl.textContent.trim() : 'Unknown';

      const termMatch = lenderName.match(/(\d+)\s*year/i);
      const loanTermMonths = termMatch ? parseInt(termMatch[1]) * 12 : 360;

      const rateEl = art.querySelector('[data-testid="rate-value"]');
      const rate = rateEl ? parseFloat((rateEl.textContent || '').replace(/[^0-9.]/g, '')) : null;

      const pmtEl = art.querySelector('[data-testid="payment-amount"]');
      const monthlyPayment = pmtEl
        ? parseFloat((pmtEl.textContent || '').replace(/[^0-9.]/g, ''))
        : null;

      const upEl =
        art.querySelector('[data-testid="upfront-costs-mobile"]') ||
        art.querySelector('[data-testid="upfront-costs-summary"]');
      let upfrontCosts = 0;
      if (upEl) {
        const raw = upEl.textContent || '';
        const m = raw.match(/\$?([\d,]+)/);
        if (m) upfrontCosts = parseFloat(m[1].replace(/,/g, '')) || 0;
      }

      if (rate === null || monthlyPayment === null || monthlyPayment <= 0) continue;

      const ptsEl = art.querySelector('[data-testid="points-value"]');
      let points = 0;
      if (ptsEl) {
        points = parseFloat((ptsEl.textContent || '').replace(/[^0-9.]/g, '')) || 0;
      }

      const displayName = points > 0
        ? `${lenderName} (${points} pt${points !== 1 ? 's' : ''})`
        : lenderName;

      lenders.push({
        lenderName: displayName,
        loanTermMonths,
        rate,
        monthlyPayment,
        upfrontCosts,
        customerScore: scoreEl
          ? parseFloat((scoreEl.textContent || '').replace(/[^0-9.]/g, ''))
          : null,
      });
    }
    return lenders;
  }

  // Derive loan amount from down payment $ and %.
  function computeLoanAmount(downPaymentDollar, downPct) {
    if (downPct <= 0) return 0;
    const homePrice = downPaymentDollar / (downPct / 100);
    return homePrice - downPaymentDollar;
  }

  // NPV of total cash outflows: down payment + upfront costs + interest.
  // Down payment and upfront are paid today (no discounting).
  // Interest is discounted by the opportunity cost of capital.
  // Also returns equity at end of projection period (down payment + principal paid).
  function computeLoanMetrics(loan, loanAmount, downPaymentDollar) {
    if (loanAmount <= 0) {
      return {
        npvCost: downPaymentDollar + loan.upfrontCosts,
        equityAt8yr: downPaymentDollar,
      };
    }

    const r = loan.rate / 100 / 12;
    const d = CONFIG.discountRate / 100 / 12;
    const months = Math.min(projectionMonths(), loan.loanTermMonths);

    let balance = loanAmount;
    let npvInterest = 0;

    for (let m = 1; m <= months; m++) {
      const interest = balance * r;
      const principal = Math.min(loan.monthlyPayment - interest, balance);
      if (d === 0) {
        npvInterest += interest;
      } else {
        npvInterest += interest / Math.pow(1 + d, m);
      }
      balance -= principal;
      if (balance <= 0) break;
    }

    const principalPaid = loanAmount - Math.max(balance, 0);
    return {
      npvCost: downPaymentDollar + loan.upfrontCosts + npvInterest,
      equityAt8yr: downPaymentDollar + principalPaid,
    };
  }

  // Total property appreciation over projection period.
  function computeAppreciation(homePrice) {
    return homePrice * (Math.pow(1 + CONFIG.appreciationRate / 100, CONFIG.projectionYears) - 1);
  }

  function renderPanel(topLoans, totalCount) {
    const existing = document.getElementById('__dp_scan_panel__');
    if (existing) existing.remove();

    const panel = document.createElement('div');
    panel.id = '__dp_scan_panel__';
    panel.style.cssText = `
      position:fixed; top:12px; right:12px; z-index:2147483647;
      background:#111; color:#eee; font:11px/1.4 -apple-system,monospace;
      padding:12px 14px; border-radius:8px; max-height:85vh; overflow:auto;
      box-shadow:0 4px 18px rgba(0,0,0,.45); width:640px;
    `;

    const fmt = (n) => '$' + Math.round(n || 0).toLocaleString();

    const rows = topLoans
      .map(
        (r, i) => `
      <tr style="background:${i === 0 ? '#1a3a1a' : 'transparent'}">
        <td style="padding:3px 5px;color:#888;">${i + 1}</td>
        <td style="padding:3px 5px;max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${r.lenderName}">${r.lenderName}</td>
        <td style="padding:3px 5px;text-align:right;">${r.percent}%</td>
        <td style="padding:3px 5px;text-align:right;">${r.rate.toFixed(3)}%</td>
        <td style="padding:3px 5px;text-align:right;font-weight:bold;${i === 0 ? 'color:#5f5;' : ''}">${fmt(r.npvCost)}</td>
        <td style="padding:3px 5px;text-align:right;color:#8cf;">${fmt(r.equityAt8yr)}</td>
        <td style="padding:3px 5px;text-align:right;color:#5d5;">${fmt(r.appreciation)}</td>
      </tr>`
      )
      .join('');

    panel.innerHTML = `
      <div style="font-weight:bold;margin-bottom:4px;display:flex;justify-content:space-between;align-items:center;">
        <span>Top ${CONFIG.topN} Loans by NPV Cost</span>
        <span id="__dp_scan_close__" style="cursor:pointer;padding:0 4px;">&#x2715;</span>
      </div>
      <div style="font-size:10px;color:#888;margin-bottom:8px;">
        ${totalCount} loans tracked &middot; Discount: ${CONFIG.discountRate}% &middot; Appreciation: ${CONFIG.appreciationRate}% &middot; Projection: ${CONFIG.projectionYears}yr &middot; Score &ge; ${MIN_SCORE}
      </div>
      <table style="border-collapse:collapse;width:100%;">
        <thead>
          <tr style="border-bottom:1px solid #444;">
            <th style="text-align:left;padding:3px 5px;">#</th>
            <th style="text-align:left;padding:3px 5px;">Lender</th>
            <th style="text-align:right;padding:3px 5px;">DP%</th>
            <th style="text-align:right;padding:3px 5px;">Rate</th>
            <th style="text-align:right;padding:3px 5px;">NPV Cost</th>
            <th style="text-align:right;padding:3px 5px;">Equity@${CONFIG.projectionYears}yr</th>
            <th style="text-align:right;padding:3px 5px;">Appreciation</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
      <div style="margin-top:8px;border-top:1px solid #444;padding-top:6px;font-size:10px;color:#888;">
        NPV = DP + upfront + discounted interest. Equity = DP + principal paid. Appreciation = home value gain.
        <br>Click bookmarklet again to scan more. Clears on page reload.
      </div>
    `;
    document.body.appendChild(panel);
    document
      .getElementById('__dp_scan_close__')
      .addEventListener('click', () => panel.remove());
  }

  // ---- main run ----
  const { percentInput, dollarInput } = findDownPaymentInputs();
  if (!percentInput) {
    console.error(
      '[DP Scan] Could not locate the down payment % input. ' +
        'Open DevTools, inspect the down payment field, and adjust findDownPaymentInputs().'
    );
    return;
  }

  let allResults = window.__dpScanResults || [];

  const newResults = [];

  for (let pct = CONFIG.startPct; pct <= CONFIG.endPct; pct += CONFIG.stepPct) {
    setNativeValue(percentInput, String(pct));
    percentInput.dispatchEvent(new Event('blur', { bubbles: true }));

    const updateBtn = findUpdateButton();
    if (updateBtn) updateBtn.click();

    await sleep(CONFIG.delayMs);

    const downPaymentDollar = dollarInput
      ? parseFloat((dollarInput.value || '').replace(/[^0-9.]/g, '')) || 0
      : 0;
    const loanAmount = computeLoanAmount(downPaymentDollar, pct);
    const homePrice = downPaymentDollar + loanAmount;
    const appreciation = computeAppreciation(homePrice);

    const lenders = collectLenderData();
    if (!lenders.length) {
      console.warn(`[DP Scan] ${pct}%: no qualifying lenders found, skipping.`);
      continue;
    }

    for (const loan of lenders) {
      const { npvCost, equityAt8yr } = computeLoanMetrics(loan, loanAmount, downPaymentDollar);
      const entry = {
        percent: pct,
        downPaymentDollar,
        loanAmount,
        homePrice,
        lenderName: loan.lenderName,
        loanTermMonths: loan.loanTermMonths,
        rate: loan.rate,
        monthlyPayment: loan.monthlyPayment,
        upfrontCosts: loan.upfrontCosts,
        customerScore: loan.customerScore,
        npvCost,
        equityAt8yr,
        appreciation,
      };
      newResults.push(entry);
      console.log(
        `[DP Scan] ${pct}% | ${loan.lenderName} → ` +
          `rate ${loan.rate.toFixed(3)}%, pmt $${loan.monthlyPayment}, ` +
          `NPV $${Math.round(npvCost).toLocaleString()}, ` +
          `equity $${Math.round(equityAt8yr).toLocaleString()}, ` +
          `appr $${Math.round(appreciation).toLocaleString()}`
      );
    }
  }

  if (!newResults.length) {
    console.error('[DP Scan] No results collected — nothing to report.');
    return;
  }

  // Merge with stored results (dedup by lender + DP%)
  for (const r of newResults) {
    const idx = allResults.findIndex(
      (e) => e.lenderName === r.lenderName && e.percent === r.percent
    );
    if (idx >= 0) allResults[idx] = r;
    else allResults.push(r);
  }

  allResults.sort((a, b) => a.npvCost - b.npvCost);
  window.__dpScanResults = allResults;

  const top = allResults.slice(0, CONFIG.topN);
  console.table(top);
  console.log(`[DP Scan] BEST:`, top[0]);
  renderPanel(top, allResults.length);
})();
