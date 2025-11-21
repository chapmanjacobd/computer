# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific aliases and functions
export PATH="$HOME/bin:$HOME/.cargo/bin:$PATH"
export GOPATH=$HOME/.go
export VISUAL=nano
export EDITOR="$VISUAL"

eval "$(dircolors)"

###-tns-completion-start-###
if [ -f /home/xk/.tnsrc ]; then
    source /home/xk/.tnsrc
fi
###-tns-completion-end-###

export HISTFILE="${XDG_STATE_HOME}"/bash/history
export LESSCHARSET=utf-8
shopt -s histappend
shopt -s cmdhist
HISTCONTROL=ignoredups
export HISTIGNORE="&:ls:[bf]g:exit"

# Settings for interactive shell only inside this block
if [[ $- == *i* ]]
then
    #Prevent Ctrl+S Freezing things
    #stty -ixon

    shopt -s cdspell
    bind "set completion-ignore-case on" # note: bind used instead of sticking these in .inputrc
    bind "set bell-style none" # no bell
    bind "set show-all-if-ambiguous On" # show list automatically, without double tab

    complete -r cd
fi

