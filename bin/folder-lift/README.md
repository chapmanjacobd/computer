# folder-lift

A Go CLI utility that traverses a directory breadth-first and collapses matched parent folders by moving their contents up one level.

## Installation

```bash
go build -o flatten main.go

```

## Usage

```bash
flatten <root-folder-path> <target-folder-names...>
```

### Example

Given this initial structure:

```text
src/
└── app/
    └── match_me/
        ├── config.json
        └── assets/
            └── logo.png

```

Running the command:

```bash
flatten ./src match_me

```

Transforms the structure to:

```text
src/
└── app/
    ├── config.json
    └── assets/
        └── logo.png

```

## Output Format

The tool prints all file and folder movements as they occur:

```text
src/app/match_me/config.json
--> src/app/config.json

src/app/match_me/assets
--> src/app/assets

```

## Testing

Run the test suite using:

```bash
go test -v ./...
```
