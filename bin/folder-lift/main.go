package main

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/alecthomas/kong"
	"github.com/chapmanjacobd/merge"
)

type CLI struct {
	Root    string   `arg:"" help:"Root directory to scan." type:"existingdir"`
	Targets []string `arg:"" help:"Folder names to match and collapse."`
	Dedupe  bool     `help:"Remove any parent folders with the same name for each given path."`
}

type MoveArgs struct {
	Root    string
	Targets map[string]bool
	Dedupe  bool
}

func main() {
	var cli CLI
	kong.Parse(&cli)

	targetMap := make(map[string]bool)
	for _, target := range cli.Targets {
		targetMap[target] = true
	}

	absRoot, err := filepath.Abs(cli.Root)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	args := MoveArgs{
		Root:    filepath.Clean(absRoot),
		Targets: targetMap,
		Dedupe:  cli.Dedupe,
	}

	if err := collapseLayers(args); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}

func collapseLayers(args MoveArgs) error {
	queue := []string{args.Root}

	for len(queue) > 0 {
		currentDir := queue[0]
		queue = queue[1:]

		if info, err := os.Stat(currentDir); err != nil {
			if os.IsNotExist(err) {
				continue
			}
			return err
		} else if !info.IsDir() {
			continue
		}

		// If the current directory itself matches a target (and isn't the root), collapse it
		isTarget := args.Targets[filepath.Base(currentDir)]
		if args.Dedupe && !isTarget {
			isTarget = hasDuplicateNameInPath(currentDir)
		}

		if currentDir != args.Root && isTarget {
			newPaths, err := liftDirectoryContents(currentDir)
			if err != nil {
				return err
			}
			// Prepend or append new paths to re-evaluate them at their new locations
			queue = append(newPaths, queue...)
			continue
		}

		entries, err := os.ReadDir(currentDir)
		if err != nil {
			return err
		}

		for _, entry := range entries {
			if entry.IsDir() {
				queue = append(queue, filepath.Join(currentDir, entry.Name()))
			}
		}
	}
	return nil
}

func liftDirectoryContents(targetDir string) ([]string, error) {
	parentDir := filepath.Dir(targetDir)

	entries, err := os.ReadDir(targetDir)
	if err != nil {
		return nil, err
	}

	var newPaths []string
	for _, entry := range entries {
		dest := filepath.Join(parentDir, entry.Name())
		fmt.Printf("%s\n--> %s\n\n", filepath.Join(targetDir, entry.Name()), dest)
		if entry.IsDir() {
			newPaths = append(newPaths, dest)
		}
	}

	cli := &merge.CLI{
		Sources:     []string{targetDir},
		Destination: parentDir,
	}
	if err := merge.Run(cli); err != nil {
		return nil, err
	}

	return newPaths, nil
}

func hasDuplicateNameInPath(p string) bool {
	base := filepath.Base(p)
	if base == string(filepath.Separator) || base == "." || base == ".." {
		return false
	}
	dir := filepath.Dir(p)
	for {
		if filepath.Base(dir) == base {
			return true
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			break
		}
		dir = parent
	}
	return false
}
