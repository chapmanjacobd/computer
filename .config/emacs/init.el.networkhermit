;; emacs

(column-number-mode 1)
(electric-pair-mode 1)
(global-auto-revert-mode 1)
(global-hl-line-mode 1)
(line-number-mode 1)
(set-default-coding-systems 'utf-8-unix)
(set-language-environment "UTF-8")
(setq auto-save-default nil)
(setq auto-save-list-file-prefix nil)
(setq inhibit-startup-screen t)
(setq make-backup-files nil)
(setq scroll-conservatively most-positive-fixnum)
(setq sentence-end-double-space nil)
(setq-default display-line-numbers t)
(setq-default display-line-numbers-width 3)
(setq-default indent-tabs-mode nil)
(setq-default show-trailing-whitespace t)
(show-paren-mode 1)

(menu-bar-mode -1)
(when (display-graphic-p)
  (scroll-bar-mode -1)
  (tool-bar-mode -1))

(setq default-frame-alist
      `((font . ,(concat "Fira Code-" (or (getenv "FONT_SIZE") "12")))
        (fullscreen . maximized)))
(set-display-table-slot standard-display-table
                        'vertical-border
                        (make-glyph-code ?│))

(unless (display-graphic-p)
  (xterm-mouse-mode 1)
  (global-set-key (kbd "<mouse-4>") 'scroll-down-line)
  (global-set-key (kbd "<mouse-5>") 'scroll-up-line))

(add-hook 'term-load-hook
          (lambda ()
            (term-set-escape-char ?\C-\\)))

(add-hook 'term-mode-hook
          (lambda ()
            (display-line-numbers-mode -1)
            (setq show-trailing-whitespace nil)))

(advice-add 'term-handle-exit :after
            (lambda (&optional process-name msg)
              (let ((win (get-buffer-window)))
                (kill-buffer)
                (ignore-errors (delete-window win)))))

(when (boundp 'native-comp-eln-load-path)
  (startup-redirect-eln-cache "~/.config/emacs/eln-cache"))

(setq treesit-extra-load-path '("~/.config/emacs/tree-sitter"))

;; library

(let ((default-directory "~/.emacs.d/lisp/community"))
  (when (file-directory-p default-directory)
    (setq load-path
          (append
           (let ((load-path (copy-sequence load-path)))
             (normal-top-level-add-to-load-path
              (delete ".." (delete "." (directory-files default-directory)))))
           load-path))))

;; package

(require 'package)
(add-to-list 'package-archives
             '("melpa" . "https://melpa.org/packages/"))
(setq package-user-dir "~/.config/emacs/elpa")
(setq package-gnupghome-dir "~/.config/emacs/elpa/gnupg")
(package-initialize)

(setq package-selected-packages '(##
                                  doom-modeline
                                  dracula-theme
                                  evil
                                  evil-collection
                                  evil-surround
                                  git-gutter
                                  go-mode
                                  magit
                                  modus-themes
                                  nord-theme
                                  rust-mode
                                  slime
                                  treesit-auto))

;; doom-modeline

(require 'doom-modeline)

(doom-modeline-mode 1)

;; evil

(setq evil-overriding-maps nil)
(setq evil-toggle-key "\C-\\")
(setq evil-want-C-h-delete t)
(setq evil-want-C-u-delete t)
(setq evil-want-C-u-scroll t)
(setq evil-want-Y-yank-to-eol t)
(setq evil-want-keybinding nil)

(require 'evil)
(require 'evil-collection)
(require 'evil-surround)

(defun visual-search (begin end type forward)
  (unless (eq type 'block)
    (let ((selection (regexp-quote (buffer-substring begin end))))
      (if (eq evil-search-module 'evil-search)
          (progn
            (setq evil-ex-search-direction (if forward 'forward 'backward))
            (setq evil-ex-search-pattern
                  (let (evil-ex-search-vim-style-regexp)
                    (evil-ex-make-search-pattern selection)))
            (unless (equal (car-safe evil-ex-search-history) selection)
              (push selection evil-ex-search-history))
            (evil-push-search-history selection forward)
            (evil-ex-search))
        (progn
          (setq isearch-forward forward)
          (evil-push-search-history selection forward)
          (evil-search selection forward t))))))

(evil-define-operator visualstar (begin end type)
  :repeat nil
  (visual-search begin end type t))

(evil-define-operator visualhashtag (begin end type)
  :repeat nil
  (visual-search begin end type nil))

(setq evil-split-window-below t)
(setq evil-start-of-line t)
(setq evil-vsplit-window-right t)

(evil-select-search-module 'evil-search-module 'evil-search)

(defun ToggleRelativeNumber ()
  (interactive)
  (if (eq display-line-numbers 'relative)
      (setq-default display-line-numbers t)
    (setq-default display-line-numbers 'relative)))

(define-key evil-ex-completion-map "\C-A" [home])
(define-key evil-insert-state-map "\C-A" [home])
(define-key evil-insert-state-map "\C-E" [end])
(define-key evil-insert-state-map "\C-L" 'evil-ex-nohighlight)
(define-key evil-normal-state-map "_" 'ToggleRelativeNumber)
(define-key evil-motion-state-map "'" 'evil-goto-mark)
(define-key evil-motion-state-map "`" 'evil-goto-mark-line)
(define-key evil-normal-state-map "K" "\C-Wn\M-Xterm")
(define-key evil-normal-state-map "Q" 'evil-quit)
(define-key evil-normal-state-map "\C-J" "\C-Wj")
(define-key evil-normal-state-map "\C-K" "\C-Wk")
(define-key evil-normal-state-map "\C-L" ":nohlsearch\C-M\M-Xredraw-display")
(define-key evil-normal-state-map "\C-N" ":bnext")
(define-key evil-normal-state-map "\C-P" ":bprevious")
(define-key evil-visual-state-map "*" 'visualstar)
(define-key evil-visual-state-map "#" 'visualhashtag)
(define-key evil-visual-state-map "M" ":sort")

(add-hook 'evil-collection-setup-hook
          (lambda (mode keymaps &rest _rest)
            (when (string= mode "term")
              (evil-collection-define-key 'insert 'term-raw-map
                "\C-J" 'windmove-down
                "\C-K" 'windmove-up
                "\C-C" 'term-send-raw))))

(evil-mode 1)
(evil-collection-init)
(global-evil-surround-mode 1)

;; git-gutter

(require 'git-gutter)

(global-git-gutter-mode 1)

;; go-mode

(require 'go-mode)

(setq gofmt-args '("-s"))
(add-hook 'before-save-hook #'gofmt-before-save)

;; magit

(setq transient-save-history nil)

;; rust-mode

(require 'rust-mode)

(setq rust-format-on-save t)

;; slime

(setq inferior-lisp-program "sbcl")
(setq slime-repl-history-file nil)

;; treesit-auto

(require 'treesit-auto)
(global-treesit-auto-mode -1)

;; theme

(require 'dracula-theme)
(require 'modus-themes)
(require 'nord-theme)

(load-theme 'modus-vivendi t)
