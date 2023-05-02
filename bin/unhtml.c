#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

/* pop culture test case:
    ./unhtml "Gangnam+Style+(%EA%B0%95%EB%82%A8%EC%8A%A4%ED%83%80%EC%9D%BC).mp4"
*/

/* fix Windows macros */
#if defined(WIN32) && !defined(_WIN32)
#define _WIN32
#endif
#if defined(UNICODE) && !defined(_UNICODE)
#define _UNICODE
#endif

#ifdef _WIN32
    #include <windows.h>
    #define PATH_SEPARATORS "/\\"
    #ifndef _UNICODE
        #error Only building for Unicode-able Windows is supported at the moment
    #else
        #include <tchar.h>
    #endif
#else
    #include <locale.h>
    #define PATH_SEPARATORS "/"
#endif

int renamefile(const char *filename, char **newfilename) {
    char *renamedfile, *renamedfilepos;
    char hexbuf[3];
    const char *filepos;
    hexbuf[2] = 0;

    /* new filename has at most as many chars as the old one as three-char
       percent expressions get compressed into one char ("%20" -> '\x20') */
    if (!(renamedfile = (char *) malloc(sizeof(char) *
      (strlen(filename) + 1)))) {
        return 1;
    }

    /* convert filename into UTF-8 string */
    renamedfilepos = renamedfile;
    for (filepos = filename; *filepos; ++filepos) {
        if (*filepos == '%') {
            strncpy(hexbuf, filepos + 1, 2);
            int escapedchar = strtol(hexbuf, NULL, 16);
            if (escapedchar && !strchr(PATH_SEPARATORS, escapedchar)) {
                *renamedfilepos++ = escapedchar;
            }
            filepos += strlen(hexbuf);
        }
        else if (*filepos == '+') {
            *renamedfilepos++ = ' ';
        }
        else {
            *renamedfilepos++ = *filepos;
        }
    }
    *renamedfilepos = 0;

    /* convert filenames into platform-specific representations and invoke
       renaming call */
#ifdef _WIN32
    /* XXX: it's assumed filename is in Windows ANSI code page */
    int unifilestrlen = MultiByteToWideChar(CP_ACP, MB_PRECOMPOSED, filename,
      -1, NULL, 0);
    int unirenamedfilestrlen = MultiByteToWideChar(CP_UTF8, 0, renamedfile,
      -1, NULL, 0);
    if (!unifilestrlen || !unirenamedfilestrlen) {
        free(renamedfile);
        return 1;
    }
    LPWSTR unifile = (WCHAR *) malloc(sizeof(WCHAR) * unifilestrlen);
    if (!unifile) {
        free(renamedfile);
        return 1;
    }
    if (MultiByteToWideChar(CP_ACP, MB_PRECOMPOSED, filename, -1, unifile,
      unifilestrlen) == 0) {
        free(renamedfile);
        free(unifile);
        return 1;
    }
    LPWSTR unirenamedfile = (WCHAR *) malloc(sizeof(WCHAR) *
      unirenamedfilestrlen);
    if (!unirenamedfile) {
        free(renamedfile);
        free(unifile);
        return 1;
    }
    if (MultiByteToWideChar(CP_UTF8, 0, renamedfile, -1, unirenamedfile,
      unirenamedfilestrlen) == 0) {
        free(renamedfile);
        free(unifile);
        free(unirenamedfile);
    }
    free(renamedfile);
    BOOL res = MoveFile(unifile, unirenamedfile);
    free(unifile);
    free(unirenamedfile);
    return res != 0 ? 0 : 1;
#else
    /* check if a locale with encoding different from UTF-8 is set */
    char *locale = setlocale(LC_CTYPE, NULL);
    const char *encoding = strchr(locale, '.');
    if (encoding) {
        encoding++;
        if (strcoll("UTF-8", encoding) == 0) {
            /* locale is UTF-8, just rename */
            int res = rename(filename, renamedfile);
            free(renamedfile);
            return res;
        } else if (!*encoding) {
            /* no encoding in locale, just rename to UTF-8 */
            int res = rename(filename, renamedfile);
            free(renamedfile);
            return res;
        } else {
            /* TODO: convert UTF-8 to encoding and rename file */
            free(renamedfile);
            errno = ENOSYS;
            return 1;
        }
    } else {
        /* no encoding in locale, just rename to UTF-8 */
        int res = rename(filename, renamedfile);
        free(renamedfile);
        return res;
    }
#endif
}

int main(int argc, char **argv) {
    int i, ret = 0;
    if (argc == 1 || strcmp("--help", argv[1]) == 0
      || strcmp("-h", argv[1]) == 0) {
        printf("usage: %s [file ...]\n", argv[0]);
        return ret;
    }
#ifndef _WIN32
    setlocale(LC_ALL, "");
#endif
    for (i = 1; i < argc; i++) {
        int fret = renamefile(argv[i], NULL);
        if (fret != 0) {
            /* TODO: also check GetLastError as well on Windows */
            fprintf(stderr, "%s: %s: %s\n", argv[0], argv[i], strerror(errno));
        }
        ret = ret | fret;
    }
    return ret;
}