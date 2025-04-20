#!/usr/bin/env python3

import argparse
import json
import sys

import requests
from dns import exception as dns_exception
from dns import resolver, zone
from library.utils import iterables


def get_ns_records(domain):
    try:
        print(f"[*] Querying NS records for {domain}...", file=sys.stderr)
        ns_records = resolver.resolve(domain, 'NS')
        nameservers = [ns.target for ns in ns_records]
        return nameservers
    except resolver.NoAnswer:
        print(f"[-] No NS records found for {domain}.", file=sys.stderr)
        return None
    except resolver.NXDOMAIN:
        print(f"[-] Domain {domain} does not exist.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[!] Error querying NS records for {domain}: {e}", file=sys.stderr)
        return None


def attempt_axfr(domain, nameservers):
    if not nameservers:
        print("[-] Cannot attempt AXFR: No nameservers provided.", file=sys.stderr)
        return None

    subdomains = set()
    axfr_successful = False

    for ns in nameservers:
        print(f"  [>] Trying nameserver: {ns}", file=sys.stderr)
        try:
            z = zone.from_xfr(resolver.resolve(ns, 'A')[0].address, domain, relativize=False)
            print(f"  [+] AXFR successful on {ns}!", file=sys.stderr)
            axfr_successful = True
            # Extract domain names from the zone
            for name, node in z.nodes.items():
                # Add the absolute domain name (converting Name object to string)
                subdomains.add(str(name).rstrip('.'))  # Remove trailing dot if present
            # Since we got a successful transfer, no need to try other NS
            break
        except dns_exception.FormError:
            print(f"  [-] AXFR failed on {ns}: Server refused zone transfer (FormError).", file=sys.stderr)
        except ConnectionRefusedError:
            print(f"  [-] AXFR failed on {ns}: Connection refused.", file=sys.stderr)
        except dns_exception.Timeout:
            print(f"  [-] AXFR failed on {ns}: Query timed out.", file=sys.stderr)
        except zone.NoSOA:
            print(f"  [-] AXFR failed on {ns}: No SOA record found.", file=sys.stderr)
        except Exception as e:
            print(f"  [-] AXFR failed on {ns}: An unexpected error occurred: {e} ({type(e).__name__})", file=sys.stderr)

    if not axfr_successful:
        print("[-] AXFR failed on all nameservers.", file=sys.stderr)
        return None

    subdomains_filtered = {sub for sub in subdomains if sub != domain and not sub.endswith('.' + domain)}
    return subdomains_filtered


def query_crtsh(domain):
    subdomains = set()
    url = f"https://crt.sh/json?q={domain}"

    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()

        if not response.text:
            print("crt.sh returned an empty response.", file=sys.stderr)
            return set()

        try:
            data = response.json()
        except json.JSONDecodeError:
            print(
                f"failed to decode JSON response from crt.sh. Response text: {response.text[:100]}...", file=sys.stderr
            )
            return set()

        if not data:
            print("no certificate transparency logs found for this domain on crt.sh.", file=sys.stderr)
            return set()

        for entry in data:
            # Extract name_value, handle potential multiple entries separated by newlines
            name_values = entry.get('name_value', '').split('\n')
            for name in name_values:
                name = name.strip().lower()
                # Check if it's a valid subdomain and not the domain itself
                if name.endswith(f".{domain}") and name != domain:
                    # Remove wildcard prefix if present
                    if name.startswith('*.'):
                        name = name[2:]
                    # Add only if it's a direct subdomain or deeper
                    if name != domain:
                        subdomains.add(name)

        print(f"[+] Found {len(subdomains)} unique subdomains via crt.sh.", file=sys.stderr)
        return subdomains

    except requests.exceptions.Timeout:
        print(f"[!] Error querying crt.sh: Request timed out.", file=sys.stderr)
        return set()
    except requests.exceptions.RequestException as e:
        print(f"[!] Error querying crt.sh: {e}", file=sys.stderr)
        return set()
    except Exception as e:
        print(f"[!] An unexpected error occurred during crt.sh query: {e}", file=sys.stderr)
        return set()


def gen_subdomains(domain):
    nameservers = get_ns_records(domain)
    if nameservers:
        axfr_subdomains = attempt_axfr(domain, nameservers)
        if axfr_subdomains:
            yield from axfr_subdomains

    crtsh_subdomains = query_crtsh(domain)
    if crtsh_subdomains:
        yield from crtsh_subdomains


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find subdomains of a domain using AXFR and crt.sh.")
    parser.add_argument("domains", nargs="+", help="The target domain name (e.g., example.com)")

    args = parser.parse_args()

    for domain in args.domains:
        domain = domain.strip('/')
        if '://' in domain:
            scheme, sep, domain = domain.rpartition('://')

        for s in iterables.ordered_set(gen_subdomains(domain)):
            print(s)
