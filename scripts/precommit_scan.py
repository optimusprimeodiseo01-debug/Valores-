import re
import sys
import subprocess

# patrones peligrosos
PATTERNS = [
    r"0x[a-fA-F0-9]{64}",       # clave privada hex
    r"PRIVATE_KEY",
    r"BEGIN PRIVATE KEY",
    r"secret",
]

def get_staged_files():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )
    return result.stdout.splitlines()

def scan_file(file):

    try:
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except:
        return []

    findings = []

    for pattern in PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            findings.append((pattern, matches[:3]))

    return findings

def main():

    files = get_staged_files()

    leaks = []

    for file in files:
        findings = scan_file(file)
        if findings:
            leaks.append((file, findings))

    if leaks:
        print("\n[BLOCKED] posible fuga de claves detectada:\n")

        for file, findings in leaks:
            print(f"archivo: {file}")
            for pattern, matches in findings:
                print(f"  patron: {pattern}")
                print(f"  ejemplo: {matches}")
            print()

        print("commit cancelado\n")
        sys.exit(1)

    print("[OK] sin fugas detectadas")
    sys.exit(0)

if __name__ == "__main__":
    main()
