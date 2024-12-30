# Defined via `source`
function git_commit_message
    function generate_commit_message
        set -l prompt_text "
Below is a diff of all changes, coming from the command:
\`\`\`
git diff --cached
\`\`\`
Write a simple, one-line commit message for this diff, with no additional commentary; just output the commit message."

        if contains -- -a $argv
            git diff HEAD | llm $prompt_text
        else
            git diff --cached | llm $prompt_text
        end
    end

    function read_input
        set -l prompt $argv[1]
        read -P $prompt reply
        echo $reply
    end

    set commit_message (generate_commit_message)

    while true
        echo -e "Proposed commit message:\n"
        echo $commit_message
        echo -e ""

        set choice (read_input "Do you want to (a)ccept, (e)dit, (r)egenerate, or (c)ancel? ")

        switch $choice
            case a A ''
                if git commit $argv -m "$commit_message"
                    return 0
                else
                    return 1
                end
            case e E
                set commit_message (read_input "Enter your commit message: ")
                if [ -n "$commit_message" ] && git commit $argv -m "$commit_message"
                    return 0
                else
                    return 1
                end
            case r R
                echo "Regenerating commit message..."
                set commit_message (generate_commit_message)
            case c C q Q
                return 1
            case '*'
                echo "Invalid choice. Please try again."
        end
    end
end
