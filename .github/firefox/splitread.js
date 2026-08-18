/**
 * Reading Tracker — bookmarklet
 * -----------------------------
 * Click once on a long article:
 *   1. Inserts a plain "Section N" heading (with an #rt-section-N anchor)
 *      roughly every 2,000 words — split at the nearest paragraph break,
 *      or if none is close by, at the nearest sentence boundary.
 *   2. Silently remembers how far down the page you scroll.
 * Come back later and, if you didn't finish, a small "Jump to last
 * position" link appears top-left. Click it, it scrolls you back and
 * disappears.
 *
 * Click the bookmarklet again on the same page to turn it off — this
 * removes the resume link and un-splits every paragraph, restoring the
 * page exactly as it was.
 *
 * Tuning knobs: TARGET_WORDS (heading spacing) and NEAR_BOUNDARY (how
 * close a paragraph break has to be before a sentence-level split is
 * used instead).
 *
 * Everything is stored in localStorage, scoped to whatever site you're
 * on. Nothing is sent anywhere.
 */
/* exported readingTrackerBookmarklet */
function readingTrackerBookmarklet() {
  (function () {
    try {
      // toggle off if already active on this page
      if (typeof window.__rtCleanup === 'function') { window.__rtCleanup(); return; }

      var PAGE_KEY = 'rt:page:' + location.href.split('#')[0];
      var TARGET_WORDS = 2000;   // insert a heading roughly every N words
      var NEAR_BOUNDARY = 200;   // if a paragraph break is within N words of the target, use it

      function loadJSON(key, fb) { try { var v = JSON.parse(localStorage.getItem(key)); return v || fb; } catch (e) { return fb; } }
      var storageWarningShown = false;
      function saveJSON(key, val) {
        try {
          localStorage.setItem(key, JSON.stringify(val));
          return true;
        } catch (e) {
          if (!storageWarningShown) {
            console.warn('Reading Tracker: unable to save progress.', e);
            storageWarningShown = true;
          }
          return false;
        }
      }
      function wc(str) { var m = (str || '').trim().match(/\S+/g); return m ? m.length : 0; }

      function findMain() {
        var sels = ['article', 'main', '[role="main"]', '#content', '.post-content', '.article-content', '.entry-content'];
        for (var i = 0; i < sels.length; i++) {
          var el = document.querySelector(sels[i]);
          if (el && wc(el.innerText) > 300) return el;
        }
        return document.body;
      }
      var mainEl = findMain();

      // find the sentence-ending word (., !, or ?) closest to a target word index within a paragraph
      function findSentenceBoundary(paraEl, targetWordIdx) {
        var walker = document.createTreeWalker(paraEl, NodeFilter.SHOW_TEXT, null);
        var node, count = 0, best = null, bestDiff = Infinity;
        while ((node = walker.nextNode())) {
          var text = node.textContent;
          var re = /\S+/g, mm;
          while ((mm = re.exec(text))) {
            count++;
            var token = mm[0];
            if (/[.!?]["')\]]*$/.test(token)) {
              var diff = Math.abs(count - targetWordIdx);
              if (diff < bestDiff) {
                bestDiff = diff;
                best = { node: node, offset: mm.index + token.length };
              }
            }
          }
        }
        return best;
      }

      // ---------- 1. insert deterministic section headings ----------
      var insertedHeadings = [];
      var splitRecords = []; // {firstHalf, secondHalf, originalHTML} — used to restore split paragraphs
      var SKIP_ANCESTOR_SEL = 'nav,aside,figure,footer,header,figcaption,blockquote,pre,code';

      var paras = Array.prototype.filter.call(mainEl.querySelectorAll('p'), function (p) {
        if (wc(p.textContent) < 3) return false;
        var bad = p.closest(SKIP_ANCESTOR_SEL);
        return !(bad && mainEl.contains(bad));
      });

      if (paras.length >= 3) {
        function makeHeading(sectionNumber) {
          var heading = document.createElement('h2');
          var secId = 'rt-section-' + sectionNumber;
          while (document.getElementById(secId)) secId += 'x';
          heading.id = secId;
          heading.style.cssText = 'margin:2.4em 0 1em!important;padding-top:1em!important;border-top:1px solid rgba(120,120,120,.35)!important;font:600 13px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important;letter-spacing:.08em!important;text-transform:uppercase!important;color:#8a8a8a!important;background:none!important;';
          var anchor = document.createElement('a');
          anchor.href = '#' + secId;
          anchor.textContent = 'Section ' + sectionNumber;
          anchor.style.cssText = 'display:block!important;color:inherit!important;text-decoration:none!important;';
          heading.appendChild(anchor);
          return heading;
        }

        var firstHeading = makeHeading(1);
        paras[0].parentNode.insertBefore(firstHeading, paras[0]);
        insertedHeadings.push(firstHeading);

        var cum = [], running = 0;
        for (var i = 0; i < paras.length; i++) { running += wc(paras[i].textContent); cum.push(running); }
        var total = running;

        var targets = [];
        for (var t = TARGET_WORDS; t < total - 300; t += TARGET_WORDS) targets.push(t);

        var n = 2;
        var lastIdx = -1;
        for (var ti = 0; ti < targets.length; ti++) {
          var target = targets[ti];
          var idx = -1;
          for (var i2 = 0; i2 < cum.length; i2++) { if (cum[i2] >= target) { idx = i2; break; } }
          if (idx === -1 || idx === lastIdx) continue; // skip if it lands back in an already-split paragraph
          lastIdx = idx;

          var startOfIdx = idx === 0 ? 0 : cum[idx - 1];
          var distBefore = target - startOfIdx;
          var distAfter = cum[idx] - target;

          var heading = makeHeading(n);

          if (Math.min(distBefore, distAfter) <= NEAR_BOUNDARY) {
            // near an existing paragraph break — use it, no text is touched
            if (distBefore <= distAfter) {
              paras[idx].parentNode.insertBefore(heading, paras[idx]);
            } else if (paras[idx].nextSibling) {
              paras[idx].parentNode.insertBefore(heading, paras[idx].nextSibling);
            } else {
              paras[idx].parentNode.appendChild(heading);
            }
          } else {
            // no nearby break — split this paragraph at the nearest sentence boundary
            var localTarget = target - startOfIdx;
            var boundary = findSentenceBoundary(paras[idx], localTarget);
            if (!boundary) {
              paras[idx].parentNode.insertBefore(heading, paras[idx]);
            } else {
              var originalHTML = paras[idx].innerHTML;
              var range = document.createRange();
              range.setStart(paras[idx], 0);
              range.setEnd(boundary.node, boundary.offset);
              var frag = range.extractContents(); // moves nodes out, doesn't lose or duplicate anything
              var firstHalf = paras[idx].cloneNode(false);
              firstHalf.removeAttribute('id');
              firstHalf.appendChild(frag);
              paras[idx].parentNode.insertBefore(firstHalf, paras[idx]);
              paras[idx].parentNode.insertBefore(heading, paras[idx]);
              splitRecords.push({ firstHalf: firstHalf, secondHalf: paras[idx], originalHTML: originalHTML });
            }
          }
          insertedHeadings.push(heading);
          n++;
        }
      }

      // ---------- 2. minimal resume link + silent progress tracking ----------
      var saved = loadJSON(PAGE_KEY, null);
      function clampProgress(value) {
        var n = Number(value);
        return isFinite(n) ? Math.min(100, Math.max(0, n)) : 0;
      }
      var prevMax = saved && typeof saved === 'object' ? clampProgress(saved.maxProgress) : 0;
      var resumeLink = null;

      if (prevMax >= 5 && prevMax < 95) {
        resumeLink = document.createElement('a');
        resumeLink.href = '#';
        resumeLink.textContent = 'Jump to last position';
        resumeLink.style.cssText = 'position:fixed!important;top:12px!important;left:12px!important;z-index:2147483647!important;background:rgba(20,20,22,.88)!important;color:#f0ece1!important;font:500 12.5px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important;padding:7px 11px!important;border-radius:8px!important;text-decoration:none!important;box-shadow:0 4px 14px rgba(0,0,0,.25)!important;opacity:.92!important;transition:opacity .4s ease!important;';
        resumeLink.addEventListener('mouseenter', function () { resumeLink.style.opacity = '1'; });
        resumeLink.addEventListener('mouseleave', function () { resumeLink.style.opacity = '.92'; });
        resumeLink.addEventListener('click', function (e) {
          e.preventDefault();
          var maxScroll = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
          var dest = Math.round((prevMax / 100) * maxScroll);
          window.scrollTo({ top: dest, behavior: 'smooth' });
          resumeLink.style.opacity = '0';
          setTimeout(function () { if (resumeLink.parentNode) resumeLink.remove(); }, 450);
        });
        document.body.appendChild(resumeLink);
      }
      var maxProgress = prevMax;
      var lastSavedProgress = prevMax;
      function pct() {
        var top = window.scrollY || document.documentElement.scrollTop;
        var h = document.documentElement.scrollHeight - window.innerHeight;
        if (h <= 0) return 100;
        return Math.min(100, Math.max(0, Math.round((top / h) * 100)));
      }
      function persist(force) {
        var p = pct();
        if (p > maxProgress) maxProgress = p;
        if (force || maxProgress !== lastSavedProgress) {
          if (saveJSON(PAGE_KEY, { maxProgress: maxProgress, timestamp: Date.now() })) {
            lastSavedProgress = maxProgress;
          }
        }
      }
      function onVisChange() { if (document.hidden) persist(true); }
      function onScroll() { persist(false); }
      function onBeforeUnload() { persist(true); }

      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('beforeunload', onBeforeUnload);
      document.addEventListener('visibilitychange', onVisChange);
      persist(true);

      // ---------- 3. toggle off: fully revert ----------
      window.__rtCleanup = function () {
        window.removeEventListener('scroll', onScroll);
        window.removeEventListener('beforeunload', onBeforeUnload);
        document.removeEventListener('visibilitychange', onVisChange);
        if (resumeLink && resumeLink.parentNode) resumeLink.remove();

        for (var i = 0; i < splitRecords.length; i++) {
          var rec = splitRecords[i];
          if (rec.secondHalf.parentNode) {
            if (rec.firstHalf.parentNode) {
              var frag2 = document.createDocumentFragment();
              while (rec.firstHalf.firstChild) frag2.appendChild(rec.firstHalf.firstChild);
              rec.secondHalf.insertBefore(frag2, rec.secondHalf.firstChild);
            }
            rec.secondHalf.normalize();
            if (rec.secondHalf.innerHTML !== rec.originalHTML) rec.secondHalf.innerHTML = rec.originalHTML;
          }
          if (rec.firstHalf.parentNode) rec.firstHalf.parentNode.removeChild(rec.firstHalf);
        }
        for (var j = 0; j < insertedHeadings.length; j++) {
          if (insertedHeadings[j].parentNode) insertedHeadings[j].parentNode.removeChild(insertedHeadings[j]);
        }
        delete window.__rtCleanup;
      };
    } catch (err) { console.error('Reading Tracker error:', err); }
  })();
}
