def "nu-complete eza when" [] {
    [[value]; ["always"] ["auto"] ["never"]]
}

def "nu-complete eza sort-field" [] {
    # name, Name, size, extension, Extension, modified, changed, accessed, created, inode, type, none
    [[value]; ["name"] ["Name"] ["extension"] ["Extension"] ["size"] ["type"] ["modified"] ["accessed"] ["created"] ["inode"] ["none"] ["date"] ["time"] ["old"] ["new"]]
}

def "nu-complete eza time-field" [] {
    # modified, accessed, created, changed
    [[value]; ["modified"] ["accessed"] ["created"] ["changed"]]
}

def "nu-complete eza time-style" [] {
    [[value]; ["default"] ["iso"] ["long-iso"] ["full-iso"] ["relative"] ["+<FORMAT>"]]
}

def "nu-complete eza color-scale" [] {
    [[value]; ["all"] ["age"] ["size"]]
}

def "nu-complete eza color-scale-mode" [] {
    [[value]; ["fixed"] ["gradient"]]
}

# A modern, maintained replacement for ls
export extern "eza" [
    path?: path                                              # folder to list
    --help                                                  # show list of command-line options
    --version(-v)                                           # show version of eza
    --oneline(-1)                                           # display one entry per line
    --long(-l)                                              # display extended file metadata as a table
    --grid(-G)                                              # display entries as a grid (default)
    --across(-x)                                            # sort the grid across, rather than downwards
    --recurse(-R)                                           # recurse into directories
    --tree(-T)                                              # recurse into directories as a tree
    --dereference(-X)                                       # dereference symbolic links when displaying information
    --classify(-F): string@"nu-complete eza when"="auto"    # display type indicator by file names
    --colour: string@"nu-complete eza when"="auto"          # when to use terminal colours
    --color: string@"nu-complete eza when"="auto"           # when to use terminal colors
    --colour-scale: string@"nu-complete eza color-scale"="all"                                          # highlight levels of 'field' distinctly
    --color-scale: string@"nu-complete eza color-scale"="all"                                           # highlight levels of 'field' distinctly
    --colour-scale-mode: string@"nu-complete eza color-scale-mode"                                      # use gradient or fixed colors in --color-scale
    --color-scale-mode: string@"nu-complete eza color-scale-mode"                                      # use gradient or fixed colors in --color-scale
    --icons: string@"nu-complete eza when"="auto"           # when to display icons
    --no-quotes                                             # don't quote file names with spaces
    --hyperlink                                             # display entries as hyperlinks
    --absolute                                              # display entries with their absolute path (on, follow, off)
    --width(-w): int                                        # set screen width in columns
    --all(-a)                                               # show hidden and 'dot' files. Use this twice to also show the '.' and '..' directories
    --almost-all(-A)                                        # equivalent to --all; included for compatibility with `ls -A`
    --list-dirs(-d)                                         # list directories as files; don't list their contents
    --level(-L): int                                        # limit the depth of recursion
    --reverse(-r)                                           # reverse the sort order
    --sort(-s): string@"nu-complete eza sort-field"         # which field to sort by
    --group-directories-first                               # list directories before other files
    --only-dirs(-D)                                         # list only directories
    --only-files(-f)                                        # list only files
    --ignore-glob(-I): string                               # glob patterns (pipe-separated) of files to ignore
    --git-ignore                                            # ignore files mentioned in '.gitignore'
    --binary(-b)                                            # list file sizes with binary prefixes
    --bytes(-B)                                             # list file sizes in bytes, without any prefixes
    --group(-g)                                             # list each file's group
    --smart-group                                           # only show group if it has a different name from owner
    --header(-h)                                            # add a header row to each column
    --links(-H)                                             # list each file's number of hard links
    --inode(-i)                                             # list each file's inode number
    --modified(-m)                                          # use the modified timestamp field
    --mounts(-M)                                            # show mount details (Linux and Mac only)
    --numeric(-n)                                           # list numeric user and group IDs
    --flags(-O)                                             # list file flags (Mac, BSD, and Windows only)
    --blocksize(-S)                                         # show size of allocated file system blocks
    --time(-t): string@"nu-complete eza time-field"         # which timestamp field to list
    --accessed(-u)                                          # use the accessed timestamp field
    --created(-U)                                           # use the created timestamp field
    --changed                                               # use the changed timestamp field
    --time-style: string@"nu-complete eza time-style"       # how to format timestamps (also a custom style '+<FORMAT>' like '+%Y-%m-%d %H:%M')
    --total-size                                            # show the size of a directory as the size of all files and directories inside (unix only)
    --no-permissions                                        # suppress the permissions field
    --octal-permissions(-o)                                 # list each file's permission in octal format
    --no-filesize                                           # suppress the filesize field
    --no-user                                               # suppress the user field
    --no-time                                               # suppress the time field
    --stdin                                                 # read file names from stdin
    --git                                                   # list each file's Git status, if tracked or ignored
    --no-git                                                # suppress Git status
    --git-repos                                             # list root of git-tree status
    --extended(-@)                                          # list each file's extended attributes and sizes
    --context(-Z)                                           # list each file's security context
]

export extern "bat" [
    ...file: path  # file to print / concatenate
    --help         # Print help (see a summary with '-h')
    -h             # Print help (see more with '--help')
    --version      # Print version
    --show-all(-A)         # Show non-printable chars like space, tab and \n
    --nonprintable-notation: string@"nu-complete nonprintable-notation" # Set notation for non-printable characters
    --plain(-p)         # Only show plain style, no decorations
    --language(-l): string@"nu-complete languages" # Explicitly set the language for syntax highlighting
    --list-languages(-L) # Display a list of supported languages for syntax highlighting
    --highlight-line: string  # <N:M> Highlight from N to M line range with a different background color
    --file-name: string # Specify the name to display for a file. Useful when piping data to bat from STDIN when bat does not otherwise know the filename
    --diff(-d)       # Only show lines that have been added/removed/modified with respect to the Git index. Checkout --diff-context=N
    --diff-context: number # Include N lines of context around added/removed/modified lines when using '--diff'
    --tabs: number   # Set the tab width to T spaces. Use a width of 0 to pass tabs through directly
    --wraps: string@"nu-complete wrap-modes"  # Specify the text-wrapping mode
    --chop-long-lines(-S) # Truncate all lines longer than screen width. Alias for '--wrap=never'
    --terminal-width: number # Explicitly set the width of the terminal instead of determining it automatically
    --number(-n)     # Only show line numbers, no other decorations
    --color: string@"nu-complete when" # Specify when to use colored output
    --italic-text: string@"nu-complete ansi italics" # Specify when to use ANSI sequences for italic text in the output
    --decorations: string@"nu-complete when" # Specify when to use the decorations that have been specified via '--style'
    --force-colorization(-f) # Alias for '--decorations=always --color=always'
    --paging: string@"nu-complete when" # Specify when to use the pager
    --pager: string  # Determine which pager is used
    --map-syntax(-m): string # <glob:syntax> Map a glob pattern to an existing syntax name
    --ignored-suffix: string # <ignored-suffix> Ignore extension. For example: 'bat --ignored-suffix ".dev" my_file.json.dev' will use JSON syntax, and ignore '.dev'
    --theme: string@"nu-complete themes" # Set the theme for syntax highlighting
    --list-themes    # Display a list of supported themes for syntax highlighting
    --style: string # Configure which elements (line numbers, file headers, grid borders, Git modifications, ..)
    --line-range(-r): string # <N:M> Only print from N to M
    --unbuffered(-u) # This option exists for POSIX-compliance reasons ('u' is for 'unbuffered'). The output is always unbuffered - this option is simply ignored
    --diagnostic     # Show diagnostic information for bug reports
    --acknowledgements  # Show acknowledgements
]

def "nu-complete nonprintable-notation" [] {
    ['unicode', 'caret']
}

def "nu-complete languages" [] {
    ^bat --list-languages
    | lines
    | parse "{value}:{description}"
}

def "nu-complete wrap-modes" [] {
    ['auto', 'never', 'character']
}

def "nu-complete when" [] {
    ['auto', 'never', 'always']
}

def "nu-complete ansi italics" [] {
    ['never', 'always']
}

def "nu-complete themes" [] {
    ^bat --list-themes
    | lines
    | parse "{value}"
}

extern "curl" [
	--abstract-unix-socket					# (HTTP) Connect through an abstract Unix domain socket
	--anyauth					# (HTTP) Use most secure authentication method automatically
	--append(-a)					# (FTP SFTP) Upload: append to the target file
	--basic					# (HTTP) Use HTTP Basic authentication
	--cacert					# (TLS) Use the specified certificate file
	--capath					# (TLS) Use the specified certificate directory
	--cert-status					# (TLS) Use Certificate Status Request (aka OCSP stapling)
	--cert-type					# (TLS) Set type of the provided client certificate
	--cert(-E)					# (TLS) Use this cert
	--ciphers					# (TLS) Specifies which ciphers to use
	--compressed-ssh					# (SCP SFTP) Enables built-in SSH compression
	--compressed					# (HTTP) Request a compressed response
	--config(-K)					# Specify a text file to read curl arguments from
	--connect-timeout					# Maximum time in seconds you allow connection to take
	--connect-to					# For a request to the given HOST1:PORT1 pair, connect to HOST2:PORT2 instead
	--continue-at(-C)					# Continue/Resume a previous file transfer at the given offset
	--cookie-jar(-c)					# (HTTP) Write all cookies to this file
	--cookie(-b)					# (HTTP) Pass the data to the HTTP server in the Cookie header
	--create-dirs					# Create dirs for -o/--output
	--crlf					# (FTP SMTP) Convert LF to CRLF in upload.  Useful for MVS (OS/390)
	--crlfile					# (TLS) Provide a file using PEM format with a Certificate Revocation List
	--data-ascii					# (HTTP) Alias for -d, --data
	--data-binary					# (HTTP) Post data exactly as specified with no processing
	--data-raw					# (HTTP) Post data like --data but without interpreting "@
	--data-urlencode					# (HTTP) Post data URL-encoded
	--data(-d)					# (HTTP) Sends the specified data in a POST request to the HTTP server
	--delegation					# (GSS/kerberos) Tell the server how much it can delegate for user creds
	--digest					# (HTTP) Enables HTTP Digest authentication
	--disable-eprt					# (FTP) Dont use EPRT and LPRT commands in active FTP
	--disable-epsv					# (FTP) Dont use EPSV in passive FTP
	--disable(-q)					# Disable curlrc
	--disallow-username-in-url					# (HTTP) Exit if passed a url containing a username
	--dns-interface					# (DNS) Send outgoing DNS requests through <interface>
	--dns-ipv4-addr					# (DNS) Bind to <ip-address> when making IPv4 DNS requests
	--dns-ipv6-addr					# (DNS) Bind to <ip-address> when making IPv6 DNS requests
	--dns-servers					# Set the list of DNS servers to use
	--doh-url					# (all) Specify which DNS-over-HTTPS (DOH) server to use to resolve hostnames
	--dump-header(-D)					# (HTTP FTP) Write the received protocol headers to the specified file
	--egd-file					# (TLS) Specify the path name to the Entropy Gathering Daemon socket
	--engine					# (TLS) Select the OpenSSL crypto engine to use for cipher operations
	--expect100-timeout					# (HTTP) Maximum time in seconds to wait for a 100-continue
	--fail-early					# Fail and exit on the first detected transfer error
	--fail(-f)					# (HTTP) Fail silently (no output at all) on server errors
	--false-start					# (TLS) Use false start during the TLS handshake
	--form-string					# (HTTP SMTP IMAP) Like --form except using value string literally
	--form(-F)					# (HTTP SMTP IMAP) Emulate pressing submit on filled-in form
	--ftp-account					# (FTP) Data for the ACCT command
	--ftp-alternative-to-user					# (FTP) If USER and PASS commands fail, send this command
	--ftp-create-dirs					# (FTP SFTP) Create missing dirs with ftp
	--ftp-method					# (FTP) Control what method curl should use to reach a file on an FTP(S) server
	--ftp-pasv					# (FTP) Use passive mode for the data connection
	--ftp-port(-P)					# (FTP) Reverses the default initiator/listener roles when connecting with FTP
	--ftp-pret					# (FTP) Tell curl to send a PRET command before PASV (and EPSV)
	--ftp-skip-pasv-ip					# (FTP) Use same IP instead of IP the server suggests in response to PASV
	--ftp-ssl-ccc-mode					# (FTP) Sets the CCC mode
	--ftp-ssl-ccc					# (FTP) Use CCC (Clear Command Channel) Shuts down the SSL/TLS layer after auth
	--ftp-ssl-control					# (FTP) Require SSL/TLS for the FTP login, clear for transfer
	--get(-G)					# Use GET instead of POST
	--globoff(-g)					# This option switches off the "URL globbing parser
	--happy-eyeballs-timeout-ms					# Attempt to connect to both IPv4 and IPv6 in parallel
	--haproxy-protocol					# (HTTP) Use HAProxy PROXY protocol
	--head(-I)					# (HTTP FTP FILE) Fetch the headers only
	--header(-H)					# (HTTP) Extra header to include in the request when sending HTTP to a server
	--help(-h)					# Usage help
	--hostpubmd5					# (SFTP SCP) Pass a string containing 32 hexadecimal digits
	# these commands break the nu's parser
	#--http0.9					# (HTTP) Accept HTTP version 0.9 response
	#--http1.0(-0)					# (HTTP) Use HTTP version 1
	#--http1.1					# (HTTP) Use HTTP version 1.1
	--http2-prior-knowledge					# (HTTP) Use HTTP/2 immediately (without trying HTTP1)
	--http2					# (HTTP) Use HTTP version 2
	--ignore-content-length					# (FTP HTTP) Ignore the Content-Length header
	--include(-i)					# Include the HTTP response headers in the output
	--insecure(-k)					# (TLS)  Allow insecure connections
	--interface					# Perform an operation using a specified interface
	--ipv4(-4)					# Use IPv4 only
	--ipv6(-6)					# Use IPv6 only
	--junk-session-cookies(-j)					# (HTTP) Discard all session cookies
	--keepalive-time					# Specify idle time before keepalive is sent
	--key-type					# (TLS) Private key file type
	--key					# (TLS SSH) Private key file name
	--krb					# (FTP) Enable Kerberos authentication and use
	--libcurl					# Write C-code equivalent to the invocation to the given file
	--limit-rate					# Limit bandwidth (Examples: 200K, 3m and 1G)
	--list-only(-l)					# (FTP POP3) (FTP) Use name-only view when listing
	--local-port					# Set a preferred single number or range (FROM-TO) of local ports to use
	--location-trusted					# (HTTP) Like -L, --location, but allow sending the name + password
	--location(-L)					# (HTTP) Follow redirects
	--login-options					# (IMAP POP3 SMTP) Specify the login options
	--mail-auth					# (SMTP) Specify a single address
	--mail-from					# (SMTP) Specify a single address that the given mail should get sent from
	--mail-rcpt					# (SMTP) Specify a single address, user name or mailing list name
	--manual(-M)					# Manual.  Display the huge help text
	--max-filesize					# Specify the maximum size (in bytes) of a file to download
	--max-redirs					# (HTTP) Set maximum number of redirection-followings allowed
	--max-time(-m)					# Maximum time in seconds that you allow the whole operation to take
	--metalink					# Process URI as Metalink file
	--negotiate					# (HTTP) Enables Negotiate (SPNEGO) authentication
	--netrc-file					# Use this netrc file
	--netrc-optional					# Make netrc optional
	--netrc(-n)					# Use ~/.netrc
	--next					# Use a separate operation for the following URL
	--no-alpn					# (HTTPS) Disable the ALPN TLS extension
	--no-buffer(-N)					# Disable the buffering of the output stream
	--no-keepalive					# Disable use of keepalive messages on the TCP connection
	--no-npn					# (HTTPS) Disable NPN TLS extension
	--no-sessionid					# (TLS) Disable use of SSL session-ID caching
	--noproxy					# Comma-separated list of hosts which do not use a proxy
	--ntlm-wb					# (HTTP) Enable NTLM, but hand over auth to separate ntlmauth binary
	--ntlm					# (HTTP) Enable NTLM authentication
	--oauth2-bearer					# (IMAP POP3 SMTP) Specify the Bearer Token for OAUTH 2
	--output(-o)					# Write output to <file> instead of stdout
	--pass					# (SSH TLS) Passphrase for the private key
	--path-as-is					# Do not handle sequences of /../ or /./ in the given URL path
	--pinnedpubkey					# (TLS) Use the specified public key file (or hashes)
	--post301					# (HTTP) Respect RFC 7231/6.4
	--post302					# (HTTP) Respect RFC 7231/6.4
	--post303					# (HTTP) Violate RFC 7231/6.4
	--preproxy					# Use the specified SOCKS proxy before connecting to HTTP(S) proxy
	--progress-bar					# Display progress as a simple progress bar
	# --progress-bar(-#)					# (this short flag breaks nu parser) Display progress as a simple progress bar
	--proto-default					# Use this protocol for any URL missing a scheme name
	--proto-redir					# Limit what protocols it may use on redirect
	--proto					# Limit what protocols it may use in the transfer
	--proxy-anyauth					# Like --anyauth but for the proxy
	--proxy-basic					# Use HTTP Basic authentication to communicate with proxy
	--proxy-cacert					# Same as --cacert but used in HTTPS proxy context
	--proxy-capath					# Same as --capath but used in HTTPS proxy context
	--proxy-cert-type					# Same as --cert-type but used in HTTPS proxy context
	--proxy-cert					# Same as -E, --cert but used in HTTPS proxy context
	--proxy-ciphers					# Same as --ciphers but used in HTTPS proxy context
	--proxy-crlfile					# Same as --crlfile but used in HTTPS proxy context
	--proxy-digest					# Use HTTP Digest authentication to communicate with proxy
	--proxy-header					# (HTTP) Extra header to include in the request when sending HTTP to a proxy
	--proxy-insecure					# Same as -k, --insecure but used in HTTPS proxy context
	--proxy-key-type					# Same as --key-type but used in HTTPS proxy context
	--proxy-key					# Same as --key but used in HTTPS proxy context
	--proxy-negotiate					# Use HTTP Negotiate authentication to communicate with proxy
	--proxy-ntlm					# Use HTTP NTLM authentication when to communicate with proxy
	--proxy-pass					# Same as --pass but used in HTTPS proxy context
	--proxy-pinnedpubkey					# (TLS) Use specified public key file or hashes to verify proxy
	--proxy-service-name					# This option allows you to change the service name for proxy negotiation
	--proxy-ssl-allow-beast					# Same as --ssl-allow-beast but used in HTTPS proxy context
	--proxy-tls13-ciphers					# (TLS) Specify cipher suites for TLS 1.3 proxy connection
	--proxy-tlsauthtype					# Same as --tlsauthtype but used in HTTPS proxy context
	--proxy-tlspassword					# Same as --tlspassword but used in HTTPS proxy context
	--proxy-tlsuser					# Same as --tlsuser but used in HTTPS proxy context
	--proxy-tlsv1					# Same as -1, --tlsv1 but used in HTTPS proxy context
	--proxy-user(-U)					# Specify the user name and password to use for proxy authentication
	--proxy(-x)					# Use the specified proxy
	# --proxy1.0					# This breaks nu parser. Use the specified HTTP 1.0 proxy
	--proxytunnel(-p)					# If HTTP proxy is used, make curl tunnel through it
	--pubkey					# (SFTP SCP) Public key file name
	--quote(-Q)					# (FTP SFTP)  Send an arbitrary command to the remote FTP or SFTP server
	--random-file					# Specify file containing random data
	--range(-r)					# (HTTP FTP SFTP FILE) Retrieve a byte range
	--raw					# (HTTP) Pass raw data (no HTTP decoding or transfer encoding)
	--referer(-e)					# (HTTP) Sends the "Referrer Page" information to the HTTP server
	--remote-header-name(-J)					# (HTTP) Save output to filename from Content-Disposition
	--remote-name-all					# For every URL write output to local file by default
	--remote-name(-O)					# Write output to a local file named like the remote file we get
	--remote-time(-R)					# Use timestamp of remote file on output
	--request-target					# (HTTP) Use an alternative request target
	--request(-X)					# (HTTP) Specifies a custom HTTP method
	--resolve					# Provide a custom address for a specific host and port pair
	--retry-connrefused					# Consider ECONNREFUSED a transient error
	--retry-delay					# Time to wait between transfer retries
	--retry-max-time					# The retry timer is reset before the first transfer attempt
	--retry					# Number of retries when transient error occurs
	--sasl-ir					# Enable initial response in SASL authentication
	--service-name					# This option allows you to change the service name for SPNEGO
	--show-error(-S)					# When used with -s, --silent, it makes curl show an error message if it fails
	--silent(-s)					# Silent or quiet mode.  Dont show progress meter or error messages
	--socks4					# Use the specified SOCKS4 proxy
	--socks4a					# Use the specified SOCKS4a proxy
	--socks5-basic					# Use username/password authentication to connect to SOCKS5 proxy
	--socks5-gssapi-nec					# As part of the GSS-API negotiation a protection mode is negotiated
	--socks5-gssapi-service					# The default service name for a socks server is rcmd/server-fqdn
	--socks5-gssapi					# Tells curl to use GSS-API authentication when connecting to a SOCKS5 proxy
	--socks5-hostname					# Use the specified SOCKS5 proxy (and let the proxy resolve the host name)
	--socks5					# Use the specified SOCKS5 proxy - but resolve the host name locally
	--speed-limit(-Y)					# Abort download if its slower than given speed (Bps) for speed-time
	--speed-time(-y)					# Abort download if its slower than speed for given speed-time (s)
	--ssl-allow-beast					# Dont work around BEAST security flaw in SSL3 and TLS1.0
	--ssl-no-revoke					# (Schannel) This option tells curl to disable certificate revocation checks
	--ssl-reqd					# (FTP IMAP POP3 SMTP) Require SSL/TLS for the connection
	--ssl					# (FTP IMAP POP3 SMTP)  Try to use SSL/TLS for the connection
	--sslv2(-2)					# (SSL) Use SSL version 2
	--sslv3(-3)					# (SSL) Use SSL version 3
	--stderr					# Redirect all writes to stderr to the specified file instead
	--styled-output					# Use bold font styles when writing HTTP headers to terminal
	--suppress-connect-headers					# Dont print response headers for CONNECT request if -p is set
	--tcp-fastopen					# Enable use of TCP Fast Open
	--tcp-nodelay					# Turn on the TCP_NODELAY option
	--telnet-option(-t)					# Pass options to the telnet protocol
	--tftp-blksize					# (TFTP) Set TFTP BLKSIZE option (must be >512)
	--tftp-no-options					# (TFTP) Tells curl not to send TFTP options requests
	--time-cond(-z)					# (HTTP FTP) Request file modified before or later than given time
	--tls-max					# (SSL) VERSION defines maximum supported TLS version
	--tls13-ciphers					# (TLS) Specifies cipher suites to use for TLS 1.3
	--tlsauthtype					# Set TLS authentication type
	--tlspassword					# Set password for use with the TLS authentication method
	--tlsuser					# Set username for use with the TLS authentication method
	# these commands break the nu's parser
	#--tlsv1.0					# (TLS) Forces curl to use TLS version 1.0
	#--tlsv1.1					# (TLS) Forces curl to use TLS version 1.1
	#--tlsv1.2					# (TLS) Forces curl to use TLS version 1.2
	#--tlsv1.3					# (TLS) Forces curl to use TLS version 1.3
	--tlsv1					# (SSL) Tells curl to use at least TLS version 1
	--tr-encoding					# (HTTP) Request compressed Transfer-Encoding, uncompress on receive
	--trace-ascii					# Enables a full trace dump of all incoming and outgoing data
	--trace-time					# Prepends a time stamp to each trace or verbose line that curl displays
	--trace					# Enables a full trace dump of all incoming and outgoing data
	--unix-socket					# (HTTP) Connect through this Unix domain socket, instead of using the network
	--upload-file(-T)					# This transfers the specified local file to the remote URL
	--url					# Specify a URL to fetch
	--use-ascii(-B)					# (FTP LDAP) Enable ASCII transfer
	--user-agent(-A)					# (HTTP)  Specify the User-Agent string to send to the HTTP server
	--user(-u)					# Specify the user name and password to use for server authentication
	--verbose(-v)					# Makes curl verbose during the operation
	--version(-V)					# Displays information about curl and the libcurl version it uses
	--write-out(-w)					# Make curl display information on stdout after a completed transfer
	--no-eprt					# for --disable-eprt
	--no-epsv					# for --disable-epsv
	--max-redir					# Set maximum number of redirects
	--xattr					# Store metadata in xattrs (like origin URL)
	...args
]

# (TLS) Set type of the provided client certificate
extern "curl PEM, DER ENG P12" [
	--abstract-unix-socket					# (HTTP) Connect through an abstract Unix domain socket
	--anyauth					# (HTTP) Use most secure authentication method automatically
	--append(-a)					# (FTP SFTP) Upload: append to the target file
	--basic					# (HTTP) Use HTTP Basic authentication
	--cacert					# (TLS) Use the specified certificate file
	--capath					# (TLS) Use the specified certificate directory
	--cert-status					# (TLS) Use Certificate Status Request (aka OCSP stapling)
	--cert-type					# (TLS) Set type of the provided client certificate
	--cert(-E)					# (TLS) Use this cert
	--ciphers					# (TLS) Specifies which ciphers to use
	--compressed-ssh					# (SCP SFTP) Enables built-in SSH compression
	--compressed					# (HTTP) Request a compressed response
	--config(-K)					# Specify a text file to read curl arguments from
	--connect-timeout					# Maximum time in seconds you allow connection to take
	--connect-to					# For a request to the given HOST1:PORT1 pair, connect to HOST2:PORT2 instead
	--continue-at(-C)					# Continue/Resume a previous file transfer at the given offset
	--cookie-jar(-c)					# (HTTP) Write all cookies to this file
	--cookie(-b)					# (HTTP) Pass the data to the HTTP server in the Cookie header
	--create-dirs					# Create dirs for -o/--output
	--crlf					# (FTP SMTP) Convert LF to CRLF in upload.  Useful for MVS (OS/390)
	--crlfile					# (TLS) Provide a file using PEM format with a Certificate Revocation List
	--data-ascii					# (HTTP) Alias for -d, --data
	--data-binary					# (HTTP) Post data exactly as specified with no processing
	--data-raw					# (HTTP) Post data like --data but without interpreting "@
	--data-urlencode					# (HTTP) Post data URL-encoded
	--data(-d)					# (HTTP) Sends the specified data in a POST request to the HTTP server
	--delegation					# (GSS/kerberos) Tell the server how much it can delegate for user creds
	--digest					# (HTTP) Enables HTTP Digest authentication
	--disable-eprt					# (FTP) Dont use EPRT and LPRT commands in active FTP
	--disable-epsv					# (FTP) Dont use EPSV in passive FTP
	--disable(-q)					# Disable curlrc
	--disallow-username-in-url					# (HTTP) Exit if passed a url containing a username
	--dns-interface					# (DNS) Send outgoing DNS requests through <interface>
	--dns-ipv4-addr					# (DNS) Bind to <ip-address> when making IPv4 DNS requests
	--dns-ipv6-addr					# (DNS) Bind to <ip-address> when making IPv6 DNS requests
	--dns-servers					# Set the list of DNS servers to use
	--doh-url					# (all) Specify which DNS-over-HTTPS (DOH) server to use to resolve hostnames
	--dump-header(-D)					# (HTTP FTP) Write the received protocol headers to the specified file
	--egd-file					# (TLS) Specify the path name to the Entropy Gathering Daemon socket
	--engine					# (TLS) Select the OpenSSL crypto engine to use for cipher operations
	--expect100-timeout					# (HTTP) Maximum time in seconds to wait for a 100-continue
	--fail-early					# Fail and exit on the first detected transfer error
	--fail(-f)					# (HTTP) Fail silently (no output at all) on server errors
	--false-start					# (TLS) Use false start during the TLS handshake
	--form-string					# (HTTP SMTP IMAP) Like --form except using value string literally
	--form(-F)					# (HTTP SMTP IMAP) Emulate pressing submit on filled-in form
	--ftp-account					# (FTP) Data for the ACCT command
	--ftp-alternative-to-user					# (FTP) If USER and PASS commands fail, send this command
	--ftp-create-dirs					# (FTP SFTP) Create missing dirs with ftp
	--ftp-method					# (FTP) Control what method curl should use to reach a file on an FTP(S) server
	--ftp-pasv					# (FTP) Use passive mode for the data connection
	--ftp-port(-P)					# (FTP) Reverses the default initiator/listener roles when connecting with FTP
	--ftp-pret					# (FTP) Tell curl to send a PRET command before PASV (and EPSV)
	--ftp-skip-pasv-ip					# (FTP) Use same IP instead of IP the server suggests in response to PASV
	--ftp-ssl-ccc-mode					# (FTP) Sets the CCC mode
	--ftp-ssl-ccc					# (FTP) Use CCC (Clear Command Channel) Shuts down the SSL/TLS layer after auth
	--ftp-ssl-control					# (FTP) Require SSL/TLS for the FTP login, clear for transfer
	--get(-G)					# Use GET instead of POST
	--globoff(-g)					# This option switches off the "URL globbing parser
	--happy-eyeballs-timeout-ms					# Attempt to connect to both IPv4 and IPv6 in parallel
	--haproxy-protocol					# (HTTP) Use HAProxy PROXY protocol
	--head(-I)					# (HTTP FTP FILE) Fetch the headers only
	--header(-H)					# (HTTP) Extra header to include in the request when sending HTTP to a server
	--help(-h)					# Usage help
	--hostpubmd5					# (SFTP SCP) Pass a string containing 32 hexadecimal digits
	# these commands break the nu's parser
	#--http0.9					# (HTTP) Accept HTTP version 0.9 response
	#--http1.0(-0)					# (HTTP) Use HTTP version 1
	#--http1.1					# (HTTP) Use HTTP version 1.1
	--http2-prior-knowledge					# (HTTP) Use HTTP/2 immediately (without trying HTTP1)
	--http2					# (HTTP) Use HTTP version 2
	--ignore-content-length					# (FTP HTTP) Ignore the Content-Length header
	--include(-i)					# Include the HTTP response headers in the output
	--insecure(-k)					# (TLS)  Allow insecure connections
	--interface					# Perform an operation using a specified interface
	--ipv4(-4)					# Use IPv4 only
	--ipv6(-6)					# Use IPv6 only
	--junk-session-cookies(-j)					# (HTTP) Discard all session cookies
	--keepalive-time					# Specify idle time before keepalive is sent
	--key-type					# (TLS) Private key file type
	--key					# (TLS SSH) Private key file name
	--krb					# (FTP) Enable Kerberos authentication and use
	--libcurl					# Write C-code equivalent to the invocation to the given file
	--limit-rate					# Limit bandwidth (Examples: 200K, 3m and 1G)
	--list-only(-l)					# (FTP POP3) (FTP) Use name-only view when listing
	--local-port					# Set a preferred single number or range (FROM-TO) of local ports to use
	--location-trusted					# (HTTP) Like -L, --location, but allow sending the name + password
	--location(-L)					# (HTTP) Follow redirects
	--login-options					# (IMAP POP3 SMTP) Specify the login options
	--mail-auth					# (SMTP) Specify a single address
	--mail-from					# (SMTP) Specify a single address that the given mail should get sent from
	--mail-rcpt					# (SMTP) Specify a single address, user name or mailing list name
	--manual(-M)					# Manual.  Display the huge help text
	--max-filesize					# Specify the maximum size (in bytes) of a file to download
	--max-redirs					# (HTTP) Set maximum number of redirection-followings allowed
	--max-time(-m)					# Maximum time in seconds that you allow the whole operation to take
	--metalink					# Process URI as Metalink file
	--negotiate					# (HTTP) Enables Negotiate (SPNEGO) authentication
	--netrc-file					# Use this netrc file
	--netrc-optional					# Make netrc optional
	--netrc(-n)					# Use ~/.netrc
	--next					# Use a separate operation for the following URL
	--no-alpn					# (HTTPS) Disable the ALPN TLS extension
	--no-buffer(-N)					# Disable the buffering of the output stream
	--no-keepalive					# Disable use of keepalive messages on the TCP connection
	--no-npn					# (HTTPS) Disable NPN TLS extension
	--no-sessionid					# (TLS) Disable use of SSL session-ID caching
	--noproxy					# Comma-separated list of hosts which do not use a proxy
	--ntlm-wb					# (HTTP) Enable NTLM, but hand over auth to separate ntlmauth binary
	--ntlm					# (HTTP) Enable NTLM authentication
	--oauth2-bearer					# (IMAP POP3 SMTP) Specify the Bearer Token for OAUTH 2
	--output(-o)					# Write output to <file> instead of stdout
	--pass					# (SSH TLS) Passphrase for the private key
	--path-as-is					# Do not handle sequences of /../ or /./ in the given URL path
	--pinnedpubkey					# (TLS) Use the specified public key file (or hashes)
	--post301					# (HTTP) Respect RFC 7231/6.4
	--post302					# (HTTP) Respect RFC 7231/6.4
	--post303					# (HTTP) Violate RFC 7231/6.4
	--preproxy					# Use the specified SOCKS proxy before connecting to HTTP(S) proxy
	--progress-bar					# Display progress as a simple progress bar
	# --progress-bar(-#)					# (this short flag breaks nu parser) Display progress as a simple progress bar
	--proto-default					# Use this protocol for any URL missing a scheme name
	--proto-redir					# Limit what protocols it may use on redirect
	--proto					# Limit what protocols it may use in the transfer
	--proxy-anyauth					# Like --anyauth but for the proxy
	--proxy-basic					# Use HTTP Basic authentication to communicate with proxy
	--proxy-cacert					# Same as --cacert but used in HTTPS proxy context
	--proxy-capath					# Same as --capath but used in HTTPS proxy context
	--proxy-cert-type					# Same as --cert-type but used in HTTPS proxy context
	--proxy-cert					# Same as -E, --cert but used in HTTPS proxy context
	--proxy-ciphers					# Same as --ciphers but used in HTTPS proxy context
	--proxy-crlfile					# Same as --crlfile but used in HTTPS proxy context
	--proxy-digest					# Use HTTP Digest authentication to communicate with proxy
	--proxy-header					# (HTTP) Extra header to include in the request when sending HTTP to a proxy
	--proxy-insecure					# Same as -k, --insecure but used in HTTPS proxy context
	--proxy-key-type					# Same as --key-type but used in HTTPS proxy context
	--proxy-key					# Same as --key but used in HTTPS proxy context
	--proxy-negotiate					# Use HTTP Negotiate authentication to communicate with proxy
	--proxy-ntlm					# Use HTTP NTLM authentication when to communicate with proxy
	--proxy-pass					# Same as --pass but used in HTTPS proxy context
	--proxy-pinnedpubkey					# (TLS) Use specified public key file or hashes to verify proxy
	--proxy-service-name					# This option allows you to change the service name for proxy negotiation
	--proxy-ssl-allow-beast					# Same as --ssl-allow-beast but used in HTTPS proxy context
	--proxy-tls13-ciphers					# (TLS) Specify cipher suites for TLS 1.3 proxy connection
	--proxy-tlsauthtype					# Same as --tlsauthtype but used in HTTPS proxy context
	--proxy-tlspassword					# Same as --tlspassword but used in HTTPS proxy context
	--proxy-tlsuser					# Same as --tlsuser but used in HTTPS proxy context
	--proxy-tlsv1					# Same as -1, --tlsv1 but used in HTTPS proxy context
	--proxy-user(-U)					# Specify the user name and password to use for proxy authentication
	--proxy(-x)					# Use the specified proxy
	#--proxy1.0					# Use the specified HTTP 1.0 proxy
	--proxytunnel(-p)					# If HTTP proxy is used, make curl tunnel through it
	--pubkey					# (SFTP SCP) Public key file name
	--quote(-Q)					# (FTP SFTP)  Send an arbitrary command to the remote FTP or SFTP server
	--random-file					# Specify file containing random data
	--range(-r)					# (HTTP FTP SFTP FILE) Retrieve a byte range
	--raw					# (HTTP) Pass raw data (no HTTP decoding or transfer encoding)
	--referer(-e)					# (HTTP) Sends the "Referrer Page" information to the HTTP server
	--remote-header-name(-J)					# (HTTP) Save output to filename from Content-Disposition
	--remote-name-all					# For every URL write output to local file by default
	--remote-name(-O)					# Write output to a local file named like the remote file we get
	--remote-time(-R)					# Use timestamp of remote file on output
	--request-target					# (HTTP) Use an alternative request target
	--request(-X)					# (HTTP) Specifies a custom HTTP method
	--resolve					# Provide a custom address for a specific host and port pair
	--retry-connrefused					# Consider ECONNREFUSED a transient error
	--retry-delay					# Time to wait between transfer retries
	--retry-max-time					# The retry timer is reset before the first transfer attempt
	--retry					# Number of retries when transient error occurs
	--sasl-ir					# Enable initial response in SASL authentication
	--service-name					# This option allows you to change the service name for SPNEGO
	--show-error(-S)					# When used with -s, --silent, it makes curl show an error message if it fails
	--silent(-s)					# Silent or quiet mode.  Dont show progress meter or error messages
	--socks4					# Use the specified SOCKS4 proxy
	--socks4a					# Use the specified SOCKS4a proxy
	--socks5-basic					# Use username/password authentication to connect to SOCKS5 proxy
	--socks5-gssapi-nec					# As part of the GSS-API negotiation a protection mode is negotiated
	--socks5-gssapi-service					# The default service name for a socks server is rcmd/server-fqdn
	--socks5-gssapi					# Tells curl to use GSS-API authentication when connecting to a SOCKS5 proxy
	--socks5-hostname					# Use the specified SOCKS5 proxy (and let the proxy resolve the host name)
	--socks5					# Use the specified SOCKS5 proxy - but resolve the host name locally
	--speed-limit(-Y)					# Abort download if its slower than given speed (Bps) for speed-time
	--speed-time(-y)					# Abort download if its slower than speed for given speed-time (s)
	--ssl-allow-beast					# Dont work around BEAST security flaw in SSL3 and TLS1.0
	--ssl-no-revoke					# (Schannel) This option tells curl to disable certificate revocation checks
	--ssl-reqd					# (FTP IMAP POP3 SMTP) Require SSL/TLS for the connection
	--ssl					# (FTP IMAP POP3 SMTP)  Try to use SSL/TLS for the connection
	--sslv2(-2)					# (SSL) Use SSL version 2
	--sslv3(-3)					# (SSL) Use SSL version 3
	--stderr					# Redirect all writes to stderr to the specified file instead
	--styled-output					# Use bold font styles when writing HTTP headers to terminal
	--suppress-connect-headers					# Dont print response headers for CONNECT request if -p is set
	--tcp-fastopen					# Enable use of TCP Fast Open
	--tcp-nodelay					# Turn on the TCP_NODELAY option
	--telnet-option(-t)					# Pass options to the telnet protocol
	--tftp-blksize					# (TFTP) Set TFTP BLKSIZE option (must be >512)
	--tftp-no-options					# (TFTP) Tells curl not to send TFTP options requests
	--time-cond(-z)					# (HTTP FTP) Request file modified before or later than given time
	--tls-max					# (SSL) VERSION defines maximum supported TLS version
	--tls13-ciphers					# (TLS) Specifies cipher suites to use for TLS 1.3
	--tlsauthtype					# Set TLS authentication type
	--tlspassword					# Set password for use with the TLS authentication method
	--tlsuser					# Set username for use with the TLS authentication method
	#--tlsv1.0					# (TLS) Forces curl to use TLS version 1.0
	#--tlsv1.1					# (TLS) Forces curl to use TLS version 1.1
	#--tlsv1.2					# (TLS) Forces curl to use TLS version 1.2
	#--tlsv1.3					# (TLS) Forces curl to use TLS version 1.3
	--tlsv1					# (SSL) Tells curl to use at least TLS version 1
	--tr-encoding					# (HTTP) Request compressed Transfer-Encoding, uncompress on receive
	--trace-ascii					# Enables a full trace dump of all incoming and outgoing data
	--trace-time					# Prepends a time stamp to each trace or verbose line that curl displays
	--trace					# Enables a full trace dump of all incoming and outgoing data
	--unix-socket					# (HTTP) Connect through this Unix domain socket, instead of using the network
	--upload-file(-T)					# This transfers the specified local file to the remote URL
	--url					# Specify a URL to fetch
	--use-ascii(-B)					# (FTP LDAP) Enable ASCII transfer
	--user-agent(-A)					# (HTTP)  Specify the User-Agent string to send to the HTTP server
	--user(-u)					# Specify the user name and password to use for server authentication
	--verbose(-v)					# Makes curl verbose during the operation
	--version(-V)					# Displays information about curl and the libcurl version it uses
	--write-out(-w)					# Make curl display information on stdout after a completed transfer
	--no-eprt					# for --disable-eprt
	--no-epsv					# for --disable-epsv
	--max-redir					# Set maximum number of redirects
	--xattr					# Store metadata in xattrs (like origin URL)
	...args
]

# Display help and exit
extern "less" [
	--help(-?)					# Display help and exit
	--search-skip-screen(-a)					# Search after end of screen
	--auto-buffers(-B)					# Disable automatic buffer allocation
	--clear-screen(-c)					# Repaint from top
	--CLEAR-SCREEN(-C)					# Clear and repaint from top
	--dumb(-d)					# Suppress error for lacking terminal capability
	--quit-at-eof(-e)					# Exit on second EOF
	--QUIT-AT-EOF(-E)					# Exit on EOF
	--force(-f)					# Open non-regular files
	--quit-if-one-screen(-F)					# Quit if file shorter than one screen
	--hilite-search(-g)					# Highlight one search target
	--HILITE-SEARCH(-G)					# No search highlighting
	--ignore-case(-i)					# Search ignores lowercase case
	--IGNORE-CASE(-I)					# Search ignores all case
	--status-column(-J)					# Display status column
	--no-lessopen(-L)					# Ignore $LESSOPEN
	--long-prompt(-m)					# Prompt with percentage
	--LONG-PROMPT(-M)					# Verbose prompt
	--line-numbers(-n)					# Display line number
	--LINE-NUMBERS(-N)					# Display line number for each line
	--quiet(-q)					# Silent mode
	--silent					# Silent mode
	--QUIET(-Q)					# Completely silent mode
	--SILENT					# Completely silent mode
	--raw-control-chars(-r)					# Display control chars
	--RAW-CONTROL-CHARS(-R)					# Display control chars, guess screen appearance
	--squeeze-blank-lines(-s)					# Multiple blank lines sqeezed
	--chop-long-lines(-S)					# Do not fold long lines
	--underline-special(-u)					# Allow backspace and carriage return
	--UNDERLINE-SPECIAL(-U)					# Allow backspace, tab and carriage return
	--version(-V)					# Display version and exit
	--hilite-unread(-w)					# Highlight first unread line on new page
	--HILITE-UNREAD(-W)					# Highlight first unread line on any movement
	--no-init(-X)					# No termcap init
	--no-keypad					# No keypad init
	--tilde(-~)					# Lines after EOF are blank
	--shift					# Characters to scroll on left/right arrows
	# this breaks the parser
	# --shift(-#)					# Characters to scroll on left/right arrows
	...args
]

# Characters to scroll on left/right arrows
extern "less 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19" [
	--help(-?)					# Display help and exit
	--search-skip-screen(-a)					# Search after end of screen
	--auto-buffers(-B)					# Disable automatic buffer allocation
	--clear-screen(-c)					# Repaint from top
	--CLEAR-SCREEN(-C)					# Clear and repaint from top
	--dumb(-d)					# Suppress error for lacking terminal capability
	--quit-at-eof(-e)					# Exit on second EOF
	--QUIT-AT-EOF(-E)					# Exit on EOF
	--force(-f)					# Open non-regular files
	--quit-if-one-screen(-F)					# Quit if file shorter than one screen
	--hilite-search(-g)					# Highlight one search target
	--HILITE-SEARCH(-G)					# No search highlighting
	--ignore-case(-i)					# Search ignores lowercase case
	--IGNORE-CASE(-I)					# Search ignores all case
	--status-column(-J)					# Display status column
	--no-lessopen(-L)					# Ignore $LESSOPEN
	--long-prompt(-m)					# Prompt with percentage
	--LONG-PROMPT(-M)					# Verbose prompt
	--line-numbers(-n)					# Display line number
	--LINE-NUMBERS(-N)					# Display line number for each line
	--quiet(-q)					# Silent mode
	--silent					# Silent mode
	--QUIET(-Q)					# Completely silent mode
	--SILENT					# Completely silent mode
	--raw-control-chars(-r)					# Display control chars
	--RAW-CONTROL-CHARS(-R)					# Display control chars, guess screen appearance
	--squeeze-blank-lines(-s)					# Multiple blank lines sqeezed
	--chop-long-lines(-S)					# Do not fold long lines
	--underline-special(-u)					# Allow backspace and carriage return
	--UNDERLINE-SPECIAL(-U)					# Allow backspace, tab and carriage return
	--version(-V)					# Display version and exit
	--hilite-unread(-w)					# Highlight first unread line on new page
	--HILITE-UNREAD(-W)					# Highlight first unread line on any movement
	--no-init(-X)					# No termcap init
	--no-keypad					# No keypad init
	--tilde(-~)					# Lines after EOF are blank
	# --shift(-#)					# Characters to scroll on left/right arrows
	...args
]
export extern nano [
	--smarthome (-A) # Enable smart home key
	--backup (-B) # Save backups of existing files
	--backupdir (-C) # Directory for saving unique backup files
	--boldtext (-D) # Use bold instead of reverse video text
	--tabstospaces (-E) # Convert typed tabs to spaces
	--multibuffer (-F) # Read a file into a new buffer by default
	--locking (-G) # Use (vim-style) lock files
	--historylog (-H) # Save & reload old search/replace strings
	--ignorercfiles (-I) # Don't look at nanorc files
	--guidestripe (-J) # Show a guiding bar at this column
	--rawsequences (-K) # Fix numeric keypad key confusion problem
	--nonewlines (-L) # Don't add an automatic newline
	--trimblanks (-M) # Trim tail spaces when hard-wrapping
	--noconvert (-N) # Don't convert files from DOS/Mac format
	--bookstyle (-O) # Leading whitespace means new paragraph
	--positionlog (-P) # Save & restore position of the cursor
	--quotestr (-Q) # Regular expression to match quoting
	--restricted (-R) # Restrict access to the filesystem
	--softwrap (-S) # Display overlong lines on multiple rows
	--tabsize (-T) # Make a tab this number of columns wide
	--quickblank (-U) # Wipe status bar upon next keystroke
	--version (-V) # Print version information and exit
	--wordbounds (-W) # Detect word boundaries more accurately
	--wordchars (-X) # Which other characters are word parts
	--syntax (-Y) # Syntax definition to use for coloring
	--zap (-Z) # Let Bsp and Del erase a marked region
	--atblanks (-a) # When soft-wrapping, do it at whitespace
	--breaklonglines (-b) # Automatically hard-wrap overlong lines
	--constantshow (-c) # Constantly show cursor position
	--rebinddelete (-d) # Fix Backspace/Delete confusion problem
	--emptyline (-e) # Keep the line below the title bar empty
	--rcfile (-f) # Use only this file for configuring nano
	--showcursor (-g) # Show cursor in file browser & help text
	--help (-h) # Show this help text and exit
	--autoindent (-i) # Automatically indent new lines
	--jumpyscrolling (-j) # Scroll per half-screen, not per line
	--cutfromcursor (-k) # Cut from cursor to end of line
	--linenumbers (-l) # Show line numbers in front of the text
	--mouse (-m) # Enable the use of the mouse
	--noread (-n) # Do not read the file (only write it)
	--operatingdir (-o) # Set operating directory
	--preserve (-p) # Preserve XON (^Q) and XOFF (^S) keys
	--indicator (-q) # Show a position+portion indicator
	--fill (-r) # Set width for hard-wrap and justify
	--speller (-s) # Use this alternative spell checker
	--saveonexit (-t) # Save changes on exit, don't prompt
	--unix (-u) # Save a file by default in Unix format
	--view (-v) # View mode (read-only)
	--nowrap (-w) # Don't hard-wrap long lines [default]
	--nohelp (-x) # Don't show the two help lines
	--afterends (-y) # Make Ctrl+Right stop at word ends
	--stateflags (-%) # Show some states on the title bar
	--minibar (-_) # Show a feedback bar at the bottom
	--zero (-0) # Hide all bars, use whole terminal
]

# author: e2dk4r

################################################################
# FUNCTIONS
################################################################

# list of supported architecture
def scoopArches [] {
  [ "32bit", "64bit" ]
}

# list of all installed apps
def scoopInstalledApps [] {
  let localAppDir = if ('SCOOP' in $env) { [$env.SCOOP, 'apps'] | path join } else { [$env.USERPROFILE, 'scoop', 'apps'] | path join }
  let localApps   = (ls $localAppDir | get name | path basename)

  let globalAppDir = if ('SCOOP_GLOBAL' in $env) { [$env.SCOOP_GLOBAL, 'apps'] | path join } else { [$env.ProgramData, 'scoop', 'apps'] | path join }
  let globalApps   = if ($globalAppDir | path exists) { ls $globalAppDir | get name | path basename }

  $localApps | append $globalApps
}

# list of all installed apps with star
def scoopInstalledAppsWithStar [] {
  scoopInstalledApps | prepend '*'
}

# list of all manifests from all buckets
def scoopAllApps [] {
  let bucketsDir = if ('SCOOP' in $env) { [ $env.SCOOP, 'buckets' ] | path join } else { [ $env.USERPROFILE, 'scoop', 'buckets' ] | path join }
  (ls -s $bucketsDir | get name) | each {|bucket| ls ([$bucketsDir, $bucket, 'bucket', '*.json'] | path join ) | get name | path basename | str substring ..-5} | flatten | uniq
}

# list of all apps that are not installed
def scoopAvailableApps [] {
  let all       = (scoopAllApps)
  let installed = (scoopInstalledApps)

  $all | where not $it in $installed
}

# list of all config options
def scoopConfigs [] {
  [
    '7ZIPEXTRACT_USE_EXTERNAL',
    'MSIEXTRACT_USE_LESSMSI',
    'NO_JUNCTIONS',
    'SCOOP_REPO',
    'SCOOP_BRANCH',
    'proxy',
    'default_architecture',
    'debug',
    'force_update',
    'show_update_log',
    'manifest_review',
    'shim',
    'rootPath',
    'globalPath',
    'cachePath',
    'gh_token',
    'virustotal_api_key',
    'cat_style',
    'ignore_running_processes',
    'private_hosts',
    'aria2-enabled',
    'aria2-warning-enabled',
    'aria2-retry-wait',
    'aria2-split',
    'aria2-max-connection-per-server',
    'aria2-min-split-size',
    'aria2-options',
  ]
}

# boolean as strings
def scoopBooleans [] {
  ["'true'", "'false'"]
}

def scoopRepos [] {
  [
    'https://github.com/ScoopInstaller/Scoop',
  ]
}

def scoopBranches [] {
  ['master', 'develop']
}

def scoopShimBuilds [] {
  [ 'kiennq', 'scoopcs', '71']
}

def scoopCommands [] {
  ^powershell -nop -nol -c "(scoop help | ConvertTo-Json -Compress)"
  | decode
  | lines
  | last
  | to text
  | from json
  | rename value description
}

def scoopAliases [] {
  ^powershell -nop -nol -c "(scoop alias list|ConvertTo-Json -Compress)"
  | decode
  | str trim
  | lines
  | last
  | to text
  | '[' + $in + ']'
  | from json
  | get Name
}

def batStyles [] {
  [ 'default', 'auto', 'full', 'plain', 'changes', 'header', 'header-filename', 'header-filesize', 'grid', 'rule', 'numbers', 'snip' ]
}

def scoopShims [] {
  let localShimDir = if ('SCOOP' in $env) { [ $env.SCOOP, 'shims' ] | path join } else if (scoop config root_path | path exists) { scoop config root_path } else { [ $env.USERPROFILE, 'scoop', 'shims' ] | path join }
  let localShims   = if ($localShimDir | path exists) { ls $localShimDir | get name | path parse | select stem extension | where extension == shim | get stem } else { [] }

  let globalShimDir = if ('SCOOP_GLOBAL' in $env) { [ $env.SCOOP_GLOBAL, 'shims' ] | path join } else if (scoop config global_path | path exists) { scoop config global_path } else { [ $env.ProgramData, 'scoop', 'shims' ] | path join }
  let globalShims   = if ($globalShimDir | path exists) { ls $globalShimDir | get name | path parse | select stem extension | where extension == shim | get stem } else { [] }

  $localShims | append $globalShims | uniq | sort
}

################################################################
# scoop
################################################################

# Windows command line installer
export extern "scoop" [
  alias?: string@scoopCommands      # available scoop commands and aliases
  --help(-h)                        # Show help for this command.
  --version(-v)                     # Show current scoop and added buckets versions
]

################################################################
# scoop list
################################################################

# Lists all installed apps, or the apps matching the supplied query.
export extern "scoop list" [
  query?: string@scoopInstalledApps # string that will be matched
  --help(-h) # Show help for this command.
]

################################################################
# scoop uninstall
################################################################

# Uninstall specified application(s).
export extern "scoop uninstall" [
  ...app: string@scoopInstalledApps # app that will be uninstalled
  --help(-h)   # Show help for this command.
  --global(-g) # Uninstall a globally installed application(s).
  --purge(-p)  # Persisted data will be removed. Normally when application is being uninstalled, the data defined in persist property/manually persisted are kept.
]

################################################################
# scoop cleanup
################################################################

# Perform cleanup on specified installed application(s) by removing old/not actively used versions.
export extern "scoop cleanup" [
  ...app: string@scoopInstalledAppsWithStar # app that will be cleaned
  --help(-h)   # Show help for this command.
  --all(-a)    # Cleanup all apps (alternative to '*')
  --global(-g) # Perform cleanup on globally installed application(s). (Include them if '*' is used)
  --cache(-k)  # Remove outdated download cache. This will keep only the latest version cached.
]

################################################################
# scoop info
################################################################

# Display information about an application.
export extern "scoop info" [
  app: string@scoopAllApps # app that will be questioned
  --verbose(-v) # Show full paths and URLs
  --help(-h)    # Show help for this command.
]

################################################################
# scoop update
################################################################

# Update installed application(s), or scoop itself.
export extern "scoop update" [
  ...app: string@scoopInstalledAppsWithStar # which apps
  --help(-h)        # Show help for this command.
  --force(-f)       # Force update even when there is not a newer version.
  --global(-g)      # Update a globally installed application(s).
  --independent(-i) # Do not install dependencies automatically.
  --no-cache(-k)    # Do not use the download cache.
  --skip(-s)        # Skip hash validation (use with caution!).
  --quiet(-q)       # Hide extraneous messages.
  --all(-a)         # Update all apps (alternative to '*')
]

################################################################
# scoop install
################################################################

# Install specific application(s).
export extern "scoop install" [
  ...app: string@scoopAvailableApps # which apps
  --arch(-a): string@scoopArches # Use the specified architecture, if the application's manifest supports it.
  --help(-h)                     # Show help for this command.
  --global(-g)                   # Install the application(s) globally.
  --independent(-i)              # Do not install dependencies automatically.
  --no-cache(-k)                 # Do not use the download cache.
  --skip(-s)                     # Skip hash validation (use with caution!).
  --no-update-scoop(-u)          # Don't update Scoop before installing if it's outdated
]

################################################################
# scoop status
################################################################

# Show status and check for new app versions.
export extern "scoop status" [
  --help(-h)  # Show help for this command.
  --local(-l) # Checks the status for only the locally installed apps, and disables remote fetching/checking for Scoop and buckets
]

################################################################
# scoop help
################################################################

# Show help for scoop
export extern "scoop help" [
  --help(-h) # Show help for this command.

  command?: string@scoopCommands # Show help for the specified command
]

################################################################
# scoop alias
################################################################

# Add, remove or list Scoop aliases
export extern "scoop alias" [
  --help(-h)  # Show help for this command.
]

# add an alias
export extern "scoop alias add" [
  name: string                    # name of the alias
  command: string                 # scoop command
  description: string             # description of the alias
]

# list all aliases
export extern "scoop alias list" [
  --verbose(-v)   # Show alias description and table headers (works only for 'list')
]

# remove an alias
export extern "scoop alias rm" [
  ...name: string@scoopAliases # alias that will be removed
]


################################################################
# scoop shim
################################################################

# Manipulate Scoop shims
export extern "scoop shim" [
  --help(-h)  # Show help for this command.
]

# add a custom shim
export extern "scoop shim add" [
  shim_name: string               # name of the shim
  command_path: path              # path to executable
  ...cmd_args                     # additional command arguments
  --global(-g)                    # Manipulate global shim(s)
]

# remove shims (CAUTION: this could remove shims added by an app manifest)
export extern "scoop shim rm" [
  ...shim_name: string@scoopShims     # shim that will be removed
  --global(-g)                        # Manipulate global shim(s)
]

# list all shims or matching shims
export extern "scoop shim list" [
  pattern?: string                # list only matching shims
  --global(-g)                    # Manipulate global shim(s)
]

# show a shim's information
export extern "scoop shim info" [
  shim_name: string@scoopShims      # shim info to retrieve
  --global(-g)                      # Manipulate global shim(s)
]

# alternate a shim's target source
export extern "scoop shim alter" [
  shim_name: string@scoopShims      # shim that will be alternated
  --global(-g)                      # Manipulate global shim(s)
]



################################################################
# scoop which
################################################################

# Locate the path to a shim/executable that was installed with Scoop (similar to 'which' on Linux)
export extern "scoop which" [
  command: string # executable name with .exe
  --help(-h)      # Show help for this command.
]

################################################################
# scoop cat
################################################################

# Show content of specified manifest.
export extern "scoop cat" [
  app: string@scoopAllApps # app that will be shown
  --help(-h)               # Show help for this command.
]

################################################################
# scoop checkup
################################################################

# Performs a series of diagnostic tests to try to identify things that may cause problems with Scoop.
export extern "scoop checkup" [
  --help(-h)  # Show help for this command.
]

################################################################
# scoop home
################################################################

# Opens the app homepage
export extern "scoop home" [
  app: string@scoopAllApps # app that will be shown
  --help(-h)               # Show help for this command.
]

################################################################
# scoop config ...
################################################################

# Get or set configuration values
export extern "scoop config" [
  --help(-h) # Show help for this command.
]

# External 7zip (from path) will be used for archives extraction.
export extern "scoop config 7ZIPEXTRACT_USE_EXTERNAL" [
  value?: string@scoopBooleans
]

# Prefer lessmsi utility over native msiexec.
export extern "scoop config MSIEXTRACT_USE_LESSMSI" [
  value?: string@scoopBooleans
]

# The 'current' version alias will not be used. Shims and shortcuts will point to specific version instead.
export extern "scoop config NO_JUNCTIONS" [
  value?: string@scoopBooleans
]

# Git repository containing scoop source code.
export extern "scoop config SCOOP_REPO" [
  value?: string@scoopRepos
]

# Allow to use different branch than master.
export extern "scoop config SCOOP_BRANCH" [
  value?: string@scoopBranches
]

# [username:password@]host:port
export extern "scoop config proxy" [
  value?: string
]

# Allow to configure preferred architecture for application installation. If not specified, architecture is determined be system.
export extern "scoop config default_architecture" [
  value?: string@scoopArches
]

# Additional and detailed output will be shown.
export extern "scoop config debug" [
  value?: string@scoopBooleans
]

# Force apps updating to bucket's version.
export extern "scoop config force_update" [
  value?: string@scoopBooleans
]

# Do not show changed commits on 'scoop update'
export extern "scoop config show_update_log" [
  value?: string@scoopBooleans
]

# Displays the manifest of every app that's about to be installed, then asks user if they wish to proceed.
export extern "scoop config manifest_review" [
  value?: string@scoopBooleans
]

# Choose scoop shim build.
export extern "scoop config shim" [
  value?: string@scoopShimBuilds
]

# Path to Scoop root directory.
export extern "scoop config root_path" [
  value?: directory
]

# Path to Scoop root directory for global apps.
export extern "scoop config global_path" [
  value?: directory
]

# For downloads, defaults to 'cache' folder under Scoop root directory.
export extern "scoop config cachePath" [
  value?: directory
]

# GitHub API token used to make authenticated requests.
export extern "scoop config gh_token" [
  value?: string
]

# API key used for uploading/scanning files using virustotal.
export extern "scoop config virustotal_api_key" [
  value?: string
]

# "scoop cat" display style. requires "bat" to be installed.
export extern "scoop config cat_style" [
  value?: string@batStyles
]

# Discard application running messages when reset, uninstall or update
export extern "scoop config ignore_running_processes" [
  value?: string@scoopBooleans
]

# Array of private hosts that need additional authentication.
export extern "scoop config private_hosts" [
  value?: string
]

# Aria2c will be used for downloading of artifacts.
export extern "scoop config aria2-enabled" [
  value?: string@scoopBooleans
]

# Disable Aria2c warning which is shown while downloading.
export extern "scoop config aria2-warning-enabled" [
  value?: string@scoopBooleans
]

# Number of seconds to wait between retries.
export extern "scoop config aria2-retry-wait" [
  value?: number
]

# Number of connections used for download.
export extern "scoop config aria2-split" [
  value?: number
]

# The maximum number of connections to one server for each download.
export extern "scoop config aria2-max-connection-per-server" [
  value?: number
]

# Downloaded files will be split by this configured size and downloaded using multiple connections.
export extern "scoop config aria2-min-split-size" [
  value?: string
]

# Array of additional aria2 options.
export extern "scoop config aria2-options" [
  value?: string
]

# Remove a configuration setting
export extern "scoop config rm" [
  name: string@scoopConfigs # app that will be removed
]

################################################################
# scoop hold
################################################################

# Hold an app to disable updates
export extern "scoop hold" [
  app: string@scoopInstalledApps # app that will be hold back
  --global(-g) # Hold globally installed apps
  --help(-h)   # Show help for this command.
]

################################################################
# scoop unhold
################################################################

# Unhold an app to enable updates
export extern "scoop unhold" [
  app: string@scoopInstalledApps # app that will be unhold back
  --global(-g) # Unhold globally installed apps
  --help(-h)   # Show help for this command.
]

################################################################
# scoop depends
################################################################

# List dependencies for an app, in the order they'll be installed
export extern "scoop depends" [
  app: string@scoopAllApps       # app in question
  --arch(-a): string@scoopArches # Use the specified architecture, if the application's manifest supports it.
  --help(-h)                     # Show help for this command.
]

################################################################
# scoop export
################################################################

# Exports installed apps, buckets (and optionally configs) in JSON format
export extern "scoop export" [
  --config(-c) # Export the Scoop configuration file too
  --help(-h)   # Show help for this command.
]

################################################################
# scoop import
################################################################

# Imports apps, buckets and configs from a Scoopfile in JSON format
export extern "scoop import" [
  file: path # path to Scoopfile
  --help(-h) # Show help for this command.
]

################################################################
# scoop reset
################################################################

# Reset an app to resolve conflicts
export extern "scoop reset" [
  app: string@scoopInstalledAppsWithStar # app that will be reset
  --all(-a)  # Reset all apps. (alternative to '*')
  --help(-h) # Show help for this command.
]

################################################################
# scoop prefix
################################################################

# Returns the path to the specified app
export extern "scoop prefix" [
  app: string@scoopInstalledApps # app in question
  --help(-h) # Show help for this command.
]

################################################################
# scoop create
################################################################

# Create a custom app manifest
export extern "scoop create" [
  url: string # url of manifest
  --help(-h)  # Show help for this command.
]

################################################################
# scoop search
################################################################

# Search available apps
export extern "scoop search" [
  query?: string # Show app names that match the query
  --help(-h)     # Show help for this command.
]

################################################################
# scoop cache ...
################################################################

# Show the download cache
export extern "scoop cache" [
  ...?apps: string@scoopInstalledAppsWithStar # apps in question
  --help(-h) # Show help for this command.
]

# Show the download cache
export extern "scoop cache show" [
  ...?apps: string@scoopInstalledAppsWithStar # apps in question
]

# Clear the download cache
export extern "scoop cache rm" [
  ...?apps: string@scoopInstalledAppsWithStar # apps in question
  --all(-a)  # Clear all apps (alternative to '*')
]

################################################################
# scoop download
################################################################

# Download apps in the cache folder and verify hashes
export extern "scoop download" [
  app?: string@scoopAvailableApps # apps in question
  --help(-h)                      # Show help for this command.
  --force(-f)                     # Force download (overwrite cache)
  --no-hash-check(-h)             # Skip hash verification (use with caution!)
  --no-update-scoop(-u)           # Don't update Scoop before downloading if it's outdated
  --arch(-a): string@scoopArches  # Use the specified architecture, if the app supports it
]

################################################################
# scoop bucket ...
################################################################

def scoopKnownBuckets [] {
  [ "main", "extras", "versions", "nirsoft", "php", "nerd-fonts", "nonportable", "java", "games" ]
}

def scoopInstalledBuckets [] {
  let bucketsDir = if ('SCOOP' in (env).name) { [ (getenv 'SCOOP'), 'buckets' ] | path join } else { [ (getenv 'USERPROFILE'), 'scoop', 'buckets' ] | path join }
  let buckets    = (ls $bucketsDir | get name | path basename)
  $buckets
}

def scoopAvailableBuckets [] {
  let known     = (scoopKnownBuckets)
  let installed = (scoopInstalledBuckets)

  $known | where not $it in $installed
}

# Add, list or remove buckets.
export extern "scoop bucket" [
  --help(-h) # Show help for this command.
]

# add a bucket
export extern "scoop bucket add" [
  name:  string@scoopAvailableBuckets # name of the bucket
  repo?: string                       # url of git repo
  --help(-h)                          # Show help for this command.
]

# list installed buckets
export extern "scoop bucket list" [
  --help(-h) # Show help for this command.
]

# list known buckets
export extern "scoop bucket known" [
  --help(-h) # Show help for this command.
]

# remove installed buckets
export extern "scoop bucket rm" [
  name: string@scoopInstalledBuckets # bucket to be removed
  --help(-h) # Show help for this command.
]

################################################################
# scoop virustotal
################################################################

# Look for app's hash or url on virustotal.com
export extern "scoop virustotal" [
  ...apps: string@scoopInstalledAppsWithStar # app to be scanned
  --all(-a)             # Check for all installed apps
  --scan(-s)            # Send download URL for analysis (and future retrieval).
  --no-depends(-n)      # By default, all dependencies are checked too. This flag avoids it.
  --no-update-scoop(-u) # Don't update Scoop before checking if it's outdated
  --passthru(-p)        # Return reports as objects
  --help(-h)            # Show help for this command.
]

export extern "ssh" [
    destination?: string@"nu-complete ssh-host"
    -4            # Forces ssh to use IPv4 addresses only.
    -6            # Forces ssh to use IPv6 addresses only.
    -A            # Enables forwarding of connections from an authentication agent such as ssh-agent(1).
    -a            # Disables forwarding of the authentication agent connection.
    -B: string    # bind_interface
    -b: string    # bind_address
    -C            # Requests compression of all data
    -c: string    # cipher_spec
    -D            # [bind_address:]port
    -E: string    # log_file
    -e            # escape_char
    -F: string    # configfile
    -f            # Requests ssh to go to background just before command execution.
    -G            # Causes ssh to print its configuration after evaluating Host and Match blocks and exit.
    -g            # Allows remote hosts to connect to local forwarded ports
    -I: string    # pkcs11
    -i: string    # identity_file
    -J: string    # destination
    -K            # Enables GSSAPI-based authentication and forwarding(delegation) of GSSAPI credentials to the server.
    -k            # Disables forwarding (delegation) of GSSAPI credentials to the server.
    -L: string    # [bind_address:]port:host:hostport / [bind_address:]port:remote_socket / local_socket:host:hostport / local_socket:remote_socket
    -l: string    # login_name
    -M            # Places the ssh client into “master” mode for connection sharing.
    -m: string    # mac_spec
    -N            # Do not execute a remote command.
    -n            # Redirects stdin from /dev/null (5) for details.
    -O: string    # ctl_cmd
    -o: string    # option
]

def "nu-complete ssh-host" [] {
    let files = [
        '/etc/ssh/ssh_config',
        '~/.ssh/config'
    ] | filter { |file| $file | path exists }

    $files | each { |file|
        let lines = $file | open | lines | str trim

        mut result = []
        for $line in $lines {
            let data = $line | parse  --regex '^Host\s+(?<host>.+)'
            if ($data | is-not-empty) {
                $result = ($result | append { 'value': ($data.host | first), 'description': "" })
                continue;
            }
            let data = $line | parse --regex '^HostName\s+(?<hostname>.+)'
            if ($data | is-not-empty) {
                let last = $result | last | update 'description' ($data.hostname | first)
                $result = ($result | drop | append $last)
            }
        }
        $result
    } | flatten
}

# This are completions for most of the flags of `ripgrep`
# There are some missing flags, but I prefer to have less flags in the completion
# given that rg has currently (14.1.0) has 103 flags

# ripgrep (rg) recursively searches the current directory for lines matching a regex pattern
export extern "rg" [
    pattern?: string                # file to print / concatenate. Use `-` to read from stdin
    --help                          # Print help (see a summary with '-h')
    -h                              # Print help (see more with '--help')
    --version                       # Print version
    --regexp(-e): string            # A pattern to search for
    --file(-f): path                # Search for patterns from the given file
    --pre: string                   # For each input PATH, this flag causes ripgrep to search the standard output of COMMAND PATH instead of the contents of PATH
    --pre-glob: string              # Include or exclude files from a preprocessor
    --search-zip(-z)                # Search in compressed files
    --case-sensitive(-s)            # Execute the search case sensitively. This is the default mode
    --crfl                          # Use CRLF line terminators (nice for Windows)
    --dfa-size-limit: number        # The upper size limit of the regex DFA
    --encoding(-E): string          # Specify the text encoding that ripgrep will use on all files searched. The default value is auto
    --engine: string@"nu-complete regex-engine" # Specify which regular expression engine to use
    --fixed-strings(-F)             # Treat all patterns as literals instead of as regular expressions
    --ignore-case(-i)               # Case insensitive match
    --invert-match(-v)              # This flag inverts matching. That is, instead of printing lines that match, ripgrep will print lines that don't match
    --line-regexp(-x)               # This is equivalent to surrounding every pattern with ^ and $
    --max-count(-m): number         # Limit the number of matching lines per file searched to NUM
    --mmap                          # When enabled, ripgrep will search using memory maps when possible. This is enabled by default when ripgrep thinks it will be faster
    --multiline(-U)                 # This flag enable searching across multiple lines
    --multiline-dotall              # This flag enables "dot all" mode in all regex patterns. This causes . to match line terminators when multiline searching is enabledThis flag enable searching across multiple lines
    --no-unicode                    # This flag disables Unicode mode for all patterns given to ripgrep
    --null-data                     #  Enabling this flag causes ripgrep to use NUL as a line terminator instead of the default of \n
    --pcre2(-P)                     # When this flag is present, ripgrep will use the PCRE2 regex engine instead of its default regex engine
    --regex-size-limit: string      # NUM+SUFFIX? The size limit of the compiled regex
    --smart-case(-S)                # This flag instructs ripgrep to searches case insensitively if the pattern is all lowercase
    --stop-on-nonmatch              # Enabling this option will cause ripgrep to stop reading a file once it encounters a non-matching line after it has encountered a matching line
    --text(-a)                      # This flag instructs ripgrep to search binary files as if they were text
    --threads(-j): number           # This flag sets the approximate number of threads to use
    --word-regexp(-w)               # This is equivalent to surrounding every pattern with \b{start-half} and \b{end-half}
    --binary                        # Enabling this flag will cause ripgrep to search binary files
    --follow(-L)                    # This flag instructs ripgrep to follow symbolic links while traversing directories
    --glob(-g): string              # Include or exclude files and directories for searching that match the given glob
    --glob-case-insensitive         # Process all glob patterns case insensitively
    --hidden(-.)                    # Search hidden files and directories. By default, hidden files and directories are skipped
    --iglob: string                 # Include/exclude paths case insensitively
    --ignore-file: path             # Specify additional ignore files
    --ignore-file-case-insensitive  # Process ignore files case insensitively
    --max-depth(-d): number         # Descend at most NUM directories
    --max-filesize: number          # Ignore files larger than NUM in size
    --no-ignore                     # Don't use ignore files
    --type(-t): string              # Only search files matching TYPE
    --type-not(-T): string          # Do not search files matching TYPE
    --after-context(-A): number     # Show NUM lines after each match
    --before-context(-B): number    # Show NUM lines before each match
    --context(-C): number           # Show NUM lines before and after each match
    --no-line-number(-N)            # Suppress line numbers
    --replace(-r): string           # Replace matches with the given text
    --only-matching(-o)             # Print only matched parts of a line
    --sort: string@"nu-complete sort-options" # Sort results in ascending order
    --sortr: string@"nu-complete sort-options" # Sort results in descending order
    --count(-c)                     # Show count of matching lines for each file
    --count-matches                 # Show count of every match for each file
    --files-with-matches(-l)        # Print the paths with at least one match
    --files-without-match           # Print the paths that contain zero matches
    --json                          # Show search results in a JSON Lines format
]

def "nu-complete regex-engine" [] {
    ['default', 'pcre2', 'auto']
}

def "nu-complete sort-options" [] {
    ['none', 'path', 'modified', 'accessed', 'created']
}
