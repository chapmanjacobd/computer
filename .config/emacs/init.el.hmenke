;; -*- lexical-binding: t; -*-
(when (< emacs-major-version 25)
  (error "Emacs is too old!"))

;; Speed up the startup
(setq gc-cons-threshold 402653184
      gc-cons-percentage 0.6
      max-lisp-eval-depth 1600
      max-specpdl-size 2500)
(defun user/reset-startup-values ()
  (setq gc-cons-threshold 16777216
        gc-cons-percentage 0.1))
(add-hook 'emacs-startup-hook 'user/reset-startup-values)

;; Focus hooks
(defun user/focus-in-hook())
(defun user/focus-out-hook()
  (garbage-collect))
(if (< emacs-major-version 27)
    (progn
      (add-hook 'focus-in-hook 'user/focus-in-hook)
      (add-hook 'focus-out-hook 'user/focus-out-hook))
  (add-function :after after-focus-change-function
                (lambda ()
                    (if (frame-focus-state)
                        (user/focus-in-hook)
                      (user/focus-out-hook)))))

;; Narrow/widen dwim
;; http://endlessparentheses.com/emacs-narrow-or-widen-dwim.html
(defun narrow-or-widen-dwim (p)
  "Widen if buffer is narrowed, narrow-dwim otherwise.
Dwim means: region, org-src-block, org-subtree, or
defun, whichever applies first. Narrowing to
org-src-block actually calls `org-edit-src-code'.

With prefix P, don't widen, just narrow even if buffer
is already narrowed."
  (interactive "P")
  (declare (interactive-only))
  (cond ((and (buffer-narrowed-p) (not p)) (widen))
        ((region-active-p)
         (narrow-to-region (region-beginning)
                           (region-end)))
        ((derived-mode-p 'org-mode)
         ;; `org-edit-src-code' is not a real narrowing
         ;; command. Remove this first conditional if
         ;; you don't want it.
         (cond ((ignore-errors (org-edit-src-code) t)
                (delete-other-windows))
               ((ignore-errors (org-narrow-to-block) t))
               (t (org-narrow-to-subtree))))
        ((derived-mode-p 'latex-mode)
         (LaTeX-narrow-to-environment))
        (t (narrow-to-defun))))

;; This line actually replaces Emacs' entire narrowing
;; keymap, that's how much I like this command. Only
;; copy it if that's what you want.
(define-key ctl-x-map "n" #'narrow-or-widen-dwim)

;; disable useless bars (from Doom Emacs)
(push '(menu-bar-lines . 0)   default-frame-alist)
(push '(tool-bar-lines . 0)   default-frame-alist)
(push '(vertical-scroll-bars) default-frame-alist)
(setq menu-bar-mode nil
      tool-bar-mode nil
      scroll-bar-mode nil)

;; disable tooltips (from Doom Emacs)
(setq use-dialog-box nil)
(when (bound-and-true-p tooltip-mode)
  (tooltip-mode -1))
(when (eq system-type 'gnu/linux)
  (setq x-gtk-use-system-tooltips nil))

;; Enable some disabled commands
(put 'upcase-region 'disabled nil)
(put 'downcase-region 'disabled nil)
(put 'narrow-to-region 'disabled nil)

(setq-default
 indent-tabs-mode nil
 fill-column 80
 use-dialog-box nil)
(setq frame-title-format
      '((:eval (if (buffer-file-name)
                   (abbreviate-file-name (buffer-file-name))
                 "%b"))
        " - Emacs"))

;; Don't write message to the minibuffer when it's active
(when (boundp 'inhibit-message)
  (defun user/inhibit-message-in-minibuffer (f &rest args)
    (let ((inhibit-message (or inhibit-message (active-minibuffer-window))))
      (apply f args)))
  (advice-add 'message :around #'user/inhibit-message-in-minibuffer))

;; I don't like typing
(defalias 'yes-or-no-p 'y-or-n-p)

;; startup
(setq-default
 inhibit-startup-screen t
 initial-scratch-message "")

;; mule (from Doom Emacs)
(set-language-environment "UTF-8")
(setq default-input-method nil)

;; simple
(setq-default
 line-number-mode t
 column-number-mode t
 visual-line-fringe-indicators '(left-curly-arrow right-curly-arrow)
 async-shell-command-display-buffer nil
 async-shell-command-buffer 'new-buffer)
(put 'overwrite-mode 'disabled t)
(global-set-key (kbd "M-SPC") 'cycle-spacing)
(global-set-key (kbd "M-z") 'zap-up-to-char)
(global-set-key (kbd "M-Z") 'zap-to-char)
;; Clashes with undo-tree
;;(define-key global-map [remap undo] 'undo-only)
;;(global-set-key (kbd "M-_") 'undo-redo) ;; backported from Emacs 28

;; backport undo-redo from Emacs 28
;; https://git.savannah.gnu.org/cgit/emacs.git/commit/?id=2645ae1222db1df270276b227e5102884466ecb0
(when (< emacs-major-version 28)
  (defun undo--last-change-was-undo-p (undo-list)
    (while (and (consp undo-list) (eq (car undo-list) nil))
      (setq undo-list (cdr undo-list)))
    (gethash undo-list undo-equiv-table))

  (defun undo-redo (&optional arg)
    "Undo the last ARG undos."
    (interactive "*p")
    (cond
     ((not (undo--last-change-was-undo-p buffer-undo-list))
      (user-error "No undo to undo"))
     (t
      (let* ((ul buffer-undo-list)
             (new-ul
              (let ((undo-in-progress t))
                (while (and (consp ul) (eq (car ul) nil))
                  (setq ul (cdr ul)))
                (primitive-undo arg ul)))
             (new-pul (undo--last-change-was-undo-p new-ul)))
        (message "Redo%s" (if undo-in-region " in region" ""))
        (setq this-command 'undo)
        (setq pending-undo-list new-pul)
        (setq buffer-undo-list new-ul))))))

;; select
(setq-default
 x-select-enable-clipboard t)

;; files
(setq-default
 backup-by-copying t
 enable-local-eval 'maybe
 enable-local-variables t)
(let ((auto-save-directory (file-name-as-directory (concat user-emacs-directory "auto-save-files")))
      (backup-directory (file-name-as-directory (concat user-emacs-directory "backups"))))
  (make-directory auto-save-directory t)
  (make-directory backup-directory t)
  (setq-default
   backup-directory-alist `(("\\`/dev/shm") ("." . ,backup-directory))
   auto-save-file-name-transforms `((".*" ,auto-save-directory t))))
;; https://debbugs.gnu.org/cgi/bugreport.cgi?bug=31908
(setq-default create-lockfiles nil)

;; cus-edit
(setq-default
 custom-file (concat user-emacs-directory "custom.el"))

;;;;comp
(setq-default
 comp-deferred-compilation-black-list '("^/usr" "^/nix")
 comp-deferred-compilation t)

;; completion
(when (fboundp 'global-completion-preview-mode)
  (global-completion-preview-mode 1))

;; autorevert
(global-auto-revert-mode 1)
(setq
 auto-revert-interval 2
 auto-revert-check-vc-info t
 global-auto-revert-non-file-buffers t
 auto-revert-verbose nil)

;; delsel
(delete-selection-mode 1)

;; paren
(setq show-paren-delay 0)
(show-paren-mode 1)

;; hippie-exp
(setq
 hippie-expand-try-functions-list
 '(try-expand-dabbrev
   try-expand-dabbrev-all-buffers
   try-expand-dabbrev-from-kill
   try-expand-all-abbrevs
   try-expand-list
   try-expand-line
   try-complete-file-name-partially
   try-complete-file-name
   try-complete-lisp-symbol-partially
   try-complete-lisp-symbol)
 hippie-expand-verbose t
 hippie-expand-dabbrev-skip-space nil
 hippie-expand-dabbrev-as-symbol t
 hippie-expand-no-restriction t)
(global-set-key [remap dabbrev-expand] 'hippie-expand)

;; cc-mode
(add-hook 'c-mode-common-hook
          (lambda()
            (setq indent-tabs-mode nil)
            (local-set-key (kbd "C-c o") 'ff-find-other-file)
            (c-set-offset 'innamespace 0)))
(setq
 c-default-style "linux"
 c-basic-offset 2)

;; Use tabs for indentation in sh-mode
;; That play better with heredocs
(define-minor-mode user/indent-tabs-mode
  "Use tabs for indentation"
  :init-value nil
  :global nil
  :lighter " Tabs"
  (setq
   indent-tabs-mode t
   tab-width 8
   sh-basic-offset 8
   backward-delete-char-untabify-method nil))
(add-hook 'sh-mode-hook 'user/indent-tabs-mode)

;; mouse
(xterm-mouse-mode 1)
(if (load "mwheel" t) (mwheel-install))
(defun track-mouse (e))
(setq mouse-sel-mode t)
(setq mouse-wheel-scroll-amount
      '(5
        ((shift) . hscroll)
        ((meta) . nil)
        ((control) . text-scale)))

;; pixel-scroll
(when (fboundp 'pixel-scroll-precision-mode)
  (pixel-scroll-precision-mode 1))

;; frame
(blink-cursor-mode 0)
;; set proper theme background for tmux
(setq frame-background-mode 'light)
;; Rebind C-z to avoid freezing
(defun user/suspend-frame ()
  (interactive)
  (if (display-graphic-p)
      (error "Cannot suspend graphical frame")
    (suspend-frame)))
(global-set-key (kbd "C-z") nil)
(global-set-key (kbd "C-x C-z") 'user/suspend-frame)

;; flyspell
;; https://emacs.stackexchange.com/questions/20206
(defun user/flyspell-local-vars ()
  (add-hook 'hack-local-variables-hook #'flyspell-buffer nil 'local))
(add-hook 'flyspell-mode-hook 'user/flyspell-local-vars)

;; shell
(setq-default shell-kill-buffer-on-exit t)

;; dired
(autoload 'dired-jump "dired-x")
(define-key ctl-x-map "\C-j" 'dired-jump)
(with-eval-after-load "dired"
  (setq user/dired-listing-switches " -ahl --group-directories-first")
  (defun user/dired-open-in-terminal ()
    (interactive)
    (let ((process-connection-type nil))
      (start-process-shell-command "xterm" "*Terminal*" "nohup xterm & exit")))
  (defun user/dired-multi-occur ()
    ;; https://lists.gnu.org/archive/html/help-gnu-emacs/2009-12/msg00112.html
    "Search string in files marked by dired."
    (interactive
     (let ((files (dired-get-marked-files)))
       (if (null files) (error "No files marked")
         (let ((string (read-string "List lines matching regexp in marked files: ")))
           (multi-occur (mapcar 'find-file files) string))))))
  (put 'dired-find-alternate-file 'disabled nil)
  (setq
   dired-listing-switches user/dired-listing-switches
   dired-use-ls-dired t
   dired-guess-shell-alist-user '((".*" "1>/dev/null 2>/dev/null nohup xdg-open"))
   dired-auto-revert-buffer t
   dired-dwin-target t)
  (add-hook 'dired-mode-hook 'dired-hide-details-mode)
  (define-key dired-mode-map [mouse-2] 'dired-mouse-find-file)
  (define-key dired-mode-map [M-up] 'dired-up-directory)
  (define-key dired-mode-map [M-down] 'dired-find-file)
  (define-key dired-mode-map (kbd "M-s O") 'user/dired-multi-occur)
  (define-key dired-mode-map (kbd "M-t") 'user/dired-open-in-terminal)

  ;; dired-x
  (require 'dired-x)
  (setq
   dired-omit-files (concat dired-omit-files "\\|\\`\\.")
   dired-omit-verbose nil)
  (add-hook 'dired-mode-hook 'dired-omit-mode)

  ;; dired-aux
  (require 'dired-aux)
  (setq
   dired-isearch-filenames 'dwim
   dired-create-destination-dirs 'ask
   dired-vc-rename-file t)

  ;; find-dired
  (require 'find-dired)
  (setq
   find-ls-option `("-ls" . ,user/dired-listing-switches)
   find-name-arg "-iname"))

;; ibuffer
(setq
 ibuffer-show-empty-filter-groups nil
 ibuffer-saved-filter-groups '(("user"
                                ("Files" (predicate . (buffer-file-name)))
                                ("Dired" (mode . dired-mode))
                                ("ERC" (mode . erc-mode))
                                ("Magit" (or
                                          (mode . magit-mode)
                                          (name . "^magit")))
                                ("Emacs" (name . "^\\*.*\\*$"))))
 ibuffer-expert t)
(add-hook 'ibuffer-mode-hook 'ibuffer-auto-mode)
(add-hook 'ibuffer-mode-hook (lambda ()
                               (ibuffer-switch-to-saved-filter-groups "user")))
(global-set-key (kbd "C-x C-b") 'ibuffer)

;; minibuffer
(setq
 enable-recursive-minibuffers t
 completions-format 'vertical
 completion-category-defaults nil
 read-file-name-completion-ignore-case t
 read-buffer-completion-ignore-case t
 completion-ignore-case t)
(add-to-list 'completion-styles 'substring)
(add-to-list 'completion-styles 'initials)

;; savehist
(setq
 savehist-file (concat user-emacs-directory "savehist")
 history-length 30000
 history-delete-duplicates t
 savehist-save-minibuffer-history t)
(savehist-mode 1)

;; recentf
(defun user/complete-recentf ()
  (interactive)
  (let ((files (mapcar 'abbreviate-file-name recentf-list)))
    (find-file (completing-read "Open recent: " files nil t))))
(setq
 recentf-max-menu-items 25
 recentf-max-saved-items 25
 recentf-exclude '((expand-file-name package-user-dir)
                   "ido.*" "recentf"
                   ".gz" ".xz" ".zip")
 recentf-filename-handlers '(abbreviate-file-name))
(add-hook 'after-init-hook 'recentf-mode)
(global-set-key (kbd "C-x C-r") 'user/complete-recentf)

;; saveplace
(save-place-mode 1)

;; isearch
(setq
 search-highlight t
 isearch-lax-whitespace t
 isearch-regexp-lax-whitespace nil
 isearch-lazy-highlight t
 isearch-lazy-count t
 lazy-count-prefix-format "(%s/%s) "
 lazy-count-suffix-format nil)

;; ffap
(ffap-bindings)

;; etags
(defun user/visit-tags-table ()
  (let ((tags-file (locate-dominating-file buffer-file-name "TAGS")))
    (when tags-file
      (message "Loading tags file: %s" tags-file)
      (visit-tags-table tags-file t))))
(add-hook 'find-file-hook 'user/visit-tags-table)
(setq tags-add-tables nil)
(setq etags-regen-tags-file
      (lambda (proj)
        (let* ((tags-directory (concat user-emacs-directory "tags"))
               (backup-directory-alist `(("." . ,tags-directory))))
          (make-backup-file-name-1 (concat proj "TAGS")))))
(when (fboundp 'etags-regen-mode)
  (add-hook 'prog-mode-hook 'etags-regen-mode))

;; xref
(when (> emacs-major-version 27)
  (setq
   xref-show-definitions-function #'xref-show-definitions-completing-read
   xref-show-xrefs-function #'xref-show-definitions-buffer
   xref-file-name-display 'project-relative))

;; icomplete
(setq
 icomplete-delay-completions-threshold 100
 icomplete-max-delay-chars 2
 icomplete-compute-delay 0.0
 icomplete-show-matches-on-no-input t
 icomplete-with-completion-tables t
 icomplete-in-buffer t
 icomplete-tidy-shadowed-file-names nil
 icomplete-hide-common-prefix nil)
(cond
 ((fboundp 'fido-vertical-mode) (fido-vertical-mode 1))
 ((fboundp 'icomplete-vertical-mode) (icomplete-vertical-mode 1))
 ((fboundp 'fido-mode) (fido-mode 1))
 (t (icomplete-mode 1)))
(define-key icomplete-minibuffer-map (kbd "<right>") 'icomplete-forward-completions)
(define-key icomplete-minibuffer-map (kbd "<down>") 'icomplete-forward-completions)
(define-key icomplete-minibuffer-map (kbd "<left>") 'icomplete-backward-completions)
(define-key icomplete-minibuffer-map (kbd "<up>") 'icomplete-backward-completions)
(define-key icomplete-minibuffer-map (kbd "C-j") 'exit-minibuffer)
(define-key icomplete-minibuffer-map (kbd "RET") 'icomplete-force-complete-and-exit)
(define-key icomplete-minibuffer-map (kbd "TAB") 'icomplete-force-complete)
(unless (fboundp 'icomplete-force-complete)
  (defalias 'icomplete-force-complete 'minibuffer-force-complete))


;; window
(setq display-buffer-alist
      '(("\\`\\*.*Completions.*\\*\\'"
         (display-buffer-in-side-window)
         (window-height . 0.3)
         (side . bottom)
         (slot . 0)
         (window-parameters . ((no-other-window . t))))
        ("\\`\\*TeX errors\\*\\'"
         (display-buffer-in-side-window)
         (window-height . 0.3)
         (side . bottom)
         (slot . 0))
        ("\\*Async Shell Command\\*.*"
         (display-buffer-no-window)
         nil)
        ("\\`\\*Org Agenda\\*\\'"
         (window-height . fit-window-to-buffer)
         nil)))
(setq window-combination-resize t)
(setq even-window-sizes 'height-only)
(setq window-sides-vertical nil)

;; winner
(winner-mode)

;; windmove
(global-set-key (kbd "C-x <right>") 'windmove-right)
(global-set-key (kbd "C-x <left>") 'windmove-left)
(global-set-key (kbd "C-x <up>") 'windmove-up)
(global-set-key (kbd "C-x <down>") 'windmove-down)

;; tramp
(setq tramp-default-method "ssh")
(add-to-list
 'backup-directory-alist
 (cons tramp-file-name-regexp
       (concat user-emacs-directory "tramp-backups/")))

;; vc
(setq
 vc-ignore-dir-regexp
 (format "\\(%s\\)\\|\\(%s\\)"
         vc-ignore-dir-regexp
         tramp-file-name-regexp)
 vc-git-grep-template "git --no-pager grep --recurse-submodules -n --break <C> -e <R> -- <F>")
(defun user/vc-git-grep (regexp)
  (interactive
   (progn
     (grep-compute-defaults)
     (list (grep-read-regexp))))
  (let ((root (vc-git-root default-directory)))
    (vc-git-grep regexp "" (if root root default-directory))))
(global-set-key (kbd "C-x v f") 'user/vc-git-grep)

;; grep
(add-hook 'grep-mode-hook (lambda ()
                            (switch-to-buffer-other-window "*grep*")))

;; ediff
(setq
 ediff-split-window-function 'split-window-horizontally
 ediff-merge-split-window-function 'split-window-horizontally
 ediff-window-setup-function 'ediff-setup-windows-plain)

;; gdb
(setq
 gdb-many-windows t
 gdb-show-main t)

;; warnings
(setq warning-suppress-types '((comp) (direnv)))

;; re-builder
(setq-default reb-re-syntax 'string)

;; sort
(defun sort-lines-nocase ()
  (interactive)
  (defvar sort-fold-case)
  (let ((sort-fold-case t))
    (call-interactively 'sort-lines)))

;; time-stamp
(setq-default
 time-stamp-format "%Y-%02m-%02d %02H:%02M:%02S"
 time-stamp-time-zone t)
(add-hook 'before-save-hook 'time-stamp)

;; whitespace
(add-hook 'prog-mode-hook (lambda ()
                            (setq show-trailing-whitespace t)))
(add-hook 'f90-mode (lambda ()
                      (highlight-lines-matching-regexp ".\\{133\\}" 'whitespace-line)))

;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;
;;;; PACKAGES ;;;;
;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;

;;;; This might be necessary on older Emacs
;; $ mkdir -pm0700 ~/.config/emacs/elpa/gnupg
;; $ gpg --keyserver keyserver.ubuntu.com --homedir ~/.config/emacs/elpa/gnupg --recv-keys 066DAFCB81E42C40
;; $ gpg --keyserver keyserver.ubuntu.com --homedir ~/.config/emacs/elpa/gnupg --recv-keys 645357D2883A0966


;; Work around Emacs bug https://debbugs.gnu.org/cgi/bugreport.cgi?bug=36725
(when (and (gnutls-available-p)
           (>= libgnutls-version 30603)
           (version<= emacs-version "26.2"))
  (setq gnutls-algorithm-priority "NORMAL:-VERS-TLS1.3"))

;; Always load the latest file (ignore outdated bytecode)
(setq load-prefer-newer t)

;; package archives
(setq package-enable-at-startup nil
      package--init-file-ensured t)
(require 'package)
(setq package-archives '(("gnu" . "https://elpa.gnu.org/packages/")
                         ("nongnu" . "https://elpa.nongnu.org/nongnu/")
                         ("melpa" . "https://melpa.org/packages/")
                         ("melpa-stable" . "https://stable.melpa.org/packages/")))
(setq package-archive-priorities '(("gnu" . 30)
                                   ("nongnu" . 20)
                                   ("melpa" . 10)
                                   ("melpa-stable" . 0)))
(custom-set-variables
 '(package-selected-packages
   '(auctex
     cdlatex
     cmake-mode
     csv-mode
     cuda-mode
     cython-mode
     d-mode
     diff-hl
     diminish
     direnv
     dockerfile-mode
     evil
     format-all
     gnuplot
     go-mode
     haskell-mode
     icomplete-vertical
     json-mode
     julia-mode
     keycast
     lua-mode
     magit
     markdown-mode
     nix-mode
     project
     proof-general
     rainbow-mode
     rust-mode
     terraform-mode
     transient
     tree-sitter
     tree-sitter-langs
     undo-tree
     use-package
     which-key
     xclip
     yaml-mode)))

(package-initialize)

(unless (package-installed-p 'use-package)
  (package-refresh-contents)
  (package-install 'use-package))

(setq use-package-always-demand (daemonp))

;; project
(when (< emacs-major-version 28)
  (use-package project
    :ensure t)

  (use-package icomplete-vertical
    :ensure t
    :pin melpa-stable
    :config
    (icomplete-vertical-mode)))

(use-package diminish
  :ensure t)

(use-package evil
  :ensure t
  :commands evil-mode
  :config
  (setq
   evil-mode-line-format '(before . mode-line-front-space)
   evil-normal-state-tag   (propertize " NORMAL "   'face '((:weight bold :background "SpringGreen" )))
   evil-insert-state-tag   (propertize " INSERT "   'face '((:weight bold :background "DeepSkyBlue1")))
   evil-replace-state-tag  (propertize " REPLACE "  'face '((:weight bold :background "red3"        )))
   evil-visual-state-tag   (propertize " VISUAL "   'face '((:weight bold :background "DarkOrange"  )))
   evil-emacs-state-tag    (propertize " EMACS "    'face '((:weight bold :background "SkyBlue2"    )))
   evil-motion-state-tag   (propertize " MOTION "   'face '((:weight bold :background "plum3"       )))
   evil-operator-state-tag (propertize " OPERATOR " 'face '((:weight bold :background "sandy brown" )))))

(use-package transient
  :ensure t
  :config
  ;; http://yummymelon.com/devnull/improving-emacs-isearch-usability-with-transient.html
  (transient-define-prefix cc/isearch-menu ()
    "isearch Menu"
    [["Edit Search String"
      ("e"
       "Edit the search string (recursive)"
       isearch-edit-string
       :transient nil)
      ("w"
       "Pull next word or character word from buffer"
       isearch-yank-word-or-char
       :transient nil)
      ("s"
       "Pull next symbol or character from buffer"
       isearch-yank-symbol-or-char
       :transient nil)
      ("l"
       "Pull rest of line from buffer"
       isearch-yank-line
       :transient nil)
      ("y"
       "Pull string from kill ring"
       isearch-yank-kill
       :transient nil)
      ("t"
       "Pull thing from buffer"
       isearch-forward-thing-at-point
       :transient nil)]

     ["Replace"
      ("q"
       "Start ‘query-replace’"
       isearch-query-replace
       :if-nil buffer-read-only
       :transient nil)
      ("x"
       "Start ‘query-replace-regexp’"
       isearch-query-replace-regexp
       :if-nil buffer-read-only
       :transient nil)]]

    [["Toggle"
      ("X"
       "Toggle regexp searching"
       isearch-toggle-regexp
       :transient nil)
      ("S"
       "Toggle symbol searching"
       isearch-toggle-symbol
       :transient nil)
      ("W"
       "Toggle word searching"
       isearch-toggle-word
       :transient nil)
      ("F"
       "Toggle case fold"
       isearch-toggle-case-fold
       :transient nil)
      ("L"
       "Toggle lax whitespace"
       isearch-toggle-lax-whitespace
       :transient nil)]

     ["Misc"
      ("o"
       "occur"
       isearch-occur
       :transient nil)]])

  (define-key isearch-mode-map (kbd "C-c s") 'cc/isearch-menu))

(use-package magit
  :ensure t
  :defer 2
  :init
  (setq magit-define-global-key-bindings 'recommended))

(use-package diff-hl
  :ensure t
  :defer 2
  :after magit
  :config
  (add-hook 'diff-hl-mode-on-hook
            (lambda ()
              (unless (window-system)
                (if (fboundp 'diff-hl-margin-local-mode)
                    (diff-hl-margin-local-mode)
                  (diff-hl-margin-mode)))))
  (global-diff-hl-mode)
  (add-hook 'magit-pre-refresh-hook 'diff-hl-magit-pre-refresh)
  (add-hook 'magit-post-refresh-hook 'diff-hl-magit-post-refresh))

(use-package xclip
  :ensure t
  :config
  (condition-case err
      (xclip-mode 1)
    (file-error (message "file-error: %S" err))))

;; AUCTeX
(defun user/align-environment ()
  "Apply align to the current environment only."
  (interactive)
  (save-excursion
    (LaTeX-mark-environment)
    (align (point) (mark))
    (pop-mark)))

(use-package tex-keywords
  :load-path "lisp")

(use-package tex
  :ensure auctex
  :config
  (setq-default
   TeX-PDF-mode t
   TeX-quote-after-quote t
   TeX-parse-self t
   ;;TeX-auto-local nil
   ;;TeX-auto-save t
   TeX-command-Show "LaTeX"
   ;;TeX-view-program-selection '((output-pdf "Zathura"))
   TeX-source-correlate-start-server t
   TeX-debug-bad-boxes t
   TeX-debug-warnings t
   TeX-display-help 'expert
   ;;TeX-error-overview-open-after-TeX-run t
   TeX-parse-all-errors t
   LaTeX-reftex-cite-format-auto-activate nil))

(use-package latex
  :ensure auctex
  :mode (("\\.cls\\'" . LaTeX-mode)
         ("\\.dtx\\'" . LaTeX-mode)
         ("\\.sty\\'" . LaTeX-mode)
         ("\\.tex\\'" . LaTeX-mode))
  :config
  ;; TeX mode enhancements

  ;; Key bindings
  (defun user/LaTeX-mode-hook ()
    (defalias 'align-environment 'user/align-environment)
    (define-key LaTeX-mode-map "\C-ca" 'align-environment)
    (define-key LaTeX-mode-map "\C-xn" nil) ;; narrow-or-widen-dwim
    (define-key LaTeX-mode-map [down-mouse-3] 'imenu))
  (add-hook 'LaTeX-mode-hook 'user/LaTeX-mode-hook)

  ;; SyncTeX
  (add-hook 'LaTeX-mode-hook 'TeX-source-correlate-mode)

  ;; LaTeX-math-mode
  (add-hook 'LaTeX-mode-hook 'LaTeX-math-mode)

  ;; Don't fontify math
  (eval-after-load "font-latex"
    '(set-face-foreground 'font-latex-math-face nil))
  (setq font-latex-fontify-script nil)

  ;; Fontify primitives
  (setq font-latex-match-function-keywords
        (mapcar #'(lambda (primitive) (list primitive ""))
                tex-keywords/primitives))

  ;; Override default indentation
  (setq LaTeX-indent-environment-list
   (quote
    (("verbatim" current-indentation)
     ("verbatim*" current-indentation)
     ("filecontents" current-indentation)
     ("filecontents*" current-indentation)
     ("lstlisting" current-indentation))))
  (add-to-list 'LaTeX-verbatim-environments "lstlisting"))

(use-package context
  :ensure auctex
  :mode (("\\.mk\\(ii\\|iv\\|vi\\|xl\\|lx\\)\\'" . ConTeXt-mode)
         ("\\.mp\\(ii\\|iv\\|vi\\|xl\\|lx\\)\\'" . metapost-mode))
  :config
  (setq ConTeXt-Mark-version "IV")
  (add-hook 'ConTeXt-mode-hook
            (lambda()
              (setq TeX-command-default "ConTeXt Full"
                    TeX-command-Show "ConTeXt Full"))))

(use-package cdlatex
  :ensure t
  :commands turn-on-cdlatex
  :init
  (setq
   cdlatex-takeover-parenthesis nil
   cdlatex-takeover-dollar nil
   cdlatex-takeover-subsuperscript nil)
  (add-hook 'cdlatex-tab-hook #'indent-for-tab-command)
  (add-hook 'LaTeX-mode-hook #'turn-on-cdlatex))

(use-package reftex
  :init
  (add-hook 'LaTeX-mode-hook 'turn-on-reftex)
  :config
  (add-hook 'reftex-load-hook 'imenu-add-menubar-index)
  (add-hook 'reftex-mode-hook 'imenu-add-menubar-index)
  (setq-default
   reftex-plug-into-AUCTeX t
   reftex-label-alist '(AMSTeX)
   reftex-insert-label-flags '("s" t)
   reftex-cite-format 'default
   reftex-cite-key-separator ", "))

(use-package bibref
  :load-path "lisp"
  :commands (bibref-from-aps
             bibref-from-doi
             bibref-from-arxiv))

;; bibtex
(use-package bibtex
  :bind (:map bibtex-mode-map
              ("C-c a" . bibref-from-aps)
              ("C-c d" . bibref-from-doi)
              ("C-c x" . bibref-from-arxiv)
              ("C-c v" . bibtex-validate)
              ("C-c s" . bibtex-sort-buffer)
              ([down-mouse-3] . imenu))
  :config
  (setq
   bibtex-align-at-equal-sign t
   bibtex-maintain-sorted-entries t))

;; direnv
(use-package direnv
  :if (executable-find "direnv")
  :ensure t
  :config
  (defun user/direnv-update-environment (&optional file-name force-summary)
    (unless (file-remote-p default-directory)
      (direnv-update-environment file-name force-summary)))
  (advice-add 'executable-find :before #'user/direnv-update-environment))

;; Language modes
(use-package cmake-mode
  :ensure t
  :mode ("\\`CMakeLists\\.txt\\'" "\\.cmake\\'"))
(use-package csv-mode
  :ensure t
  :mode "\\.csv\\'")
(use-package cuda-mode
  :ensure t
  :mode "\\.cu\\'")
(use-package cython-mode
  :ensure t
  :mode ("\\.pxd\\'" "\\.pyx\\'"))
(use-package d-mode
  :ensure t
  :mode "\\.d\\'")
(use-package dockerfile-mode
  :ensure t
  :mode ("\\dockerfile\\'"))
(use-package format-all
  :ensure t
  :commands format-all-mode
  :hook (prog-mode . format-all-mode)
  :config
  (define-format-all-formatter
   findent-octopus
   (:executable "findent-octopus")
   (:install)
   (:languages "Fortran Free Form")
   (:features)
   (:format (format-all--buffer-easy executable)))
  (setq-default format-all-formatters
                '(("Fortran Free Form" (findent-octopus "-i2" "-c2")))))
(use-package gnuplot
  :ensure t
  :mode ("\\.gnuplot\\'" . gnuplot-mode)
  :config (setq gnuplot-display-process nil))
(use-package go-mode
  :ensure t
  :mode "\\.go\\'"
  :config
  (add-hook 'before-save-hook 'gofmt-before-save))
(use-package haskell-mode
  :ensure t
  :mode "\\.hs\\'")
(use-package json-mode
  :ensure t
  :mode "\\.json\\'")
(use-package julia-mode
  :ensure t
  :mode "\\.jl\\'")
(use-package lua-mode
  :ensure t
  :mode ("\\.lua\\'" "\\.Quanty\\'")
  :config (setq lua-indent-level 4))
(use-package markdown-mode
  :ensure t
  :commands (markdown-mode gfm-mode)
  :mode (("\\`README\\.md\\'" . gfm-mode)
         ("\\.md\\'" . markdown-mode)
         ("\\.markdown\\'" . markdown-mode))
  :init (setq markdown-command "pandoc"))
(use-package nix-mode
  :ensure t
  :mode "\\.nix\\'")
(use-package proof-general
  :ensure t)
(use-package rust-mode
  :ensure t
  :mode "\\.rs\\'")
(use-package terraform-mode
  :ensure t)
(use-package yaml-mode
  :ensure t
  :mode ("\\.yml\\'" "\\.yaml\\'" "\\.sls\\'"))

(use-package rainbow-mode
  :ensure t
  :commands (rainbow-mode))

;; Tree-sitter needs dynamic module loading
(when (and (functionp 'module-load) (bound-and-true-p module-file-suffix))
  (use-package tree-sitter
    :ensure t
    :config (global-tree-sitter-mode))
  (use-package tree-sitter-langs
    :ensure t
    :after tree-sitter
    :config (add-hook 'tree-sitter-after-on-hook #'tree-sitter-hl-mode)))

;; Editing plugins
(use-package undo-tree
  :diminish undo-tree-mode
  :ensure t
  :config
  (setq
   undo-tree-auto-save-history t
   undo-tree-history-directory-alist `(("\\`/dev/shm") ("." . ,(concat user-emacs-directory "undo")))
   undo-tree-enable-undo-in-region t)
  (global-undo-tree-mode 1))

;; Show suggestions for incomplete key chords
(use-package which-key
  :diminish which-key-mode
  :ensure t
  :defer 2
  :config (which-key-mode 1))

(use-package keycast
  :ensure t)

;; GPT

(unless (< emacs-major-version 27)
  (use-package gptel
    :ensure t
    :config
    (setq
     gptel-backend (gptel-make-openai "SAIA"
                     :protocol "https"
                     :host "chat-ai.academiccloud.de"
                     :key (auth-source-pick-first-password :host "chat-ai.academiccloud.de")
                     :models '("openai-gpt-oss-120b")))))
