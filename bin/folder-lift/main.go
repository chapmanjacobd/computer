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
}

type MoveArgs struct {
	Root    string
	Targets map[string]bool
}

func main() {
	var cli CLI
	kong.Parse(&cli)

	targetMap := make(map[string]bool)
	for _, target := range cli.Targets {
		targetMap[target] = true
	}

	args := MoveArgs{
		Root:    filepath.Clean(cli.Root),
		Targets: targetMap,
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

		// If the current directory itself matches a target (and isn't the root), collapse it
		if currentDir != args.Root && args.Targets[filepath.Base(currentDir)] {
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

	// Use a temporary name to avoid namespace collisions during nested collapses
	tmpTargetDir := targetDir + "_collapsing_tmp"
	if err := os.Rename(targetDir, tmpTargetDir); err != nil {
		return nil, err
	}

	entries, err := os.ReadDir(tmpTargetDir)
	if err != nil {
		return nil, err
	}

	var newPaths []string

	for _, entry := range entries {
		src := filepath.Join(tmpTargetDir, entry.Name())
		dest := filepath.Join(parentDir, entry.Name())

		fmt.Printf("%s\n--> %s\n\n", filepath.Join(targetDir, entry.Name()), dest)
		cli := &merge.CLI{
			Sources:     []string{src},
			Destination: dest,
		}
		if err := merge.Run(cli); err != nil {
			return nil, err
		}

		if entry.IsDir() {
			newPaths = append(newPaths, dest)
		}
	}

	if err := os.Remove(tmpTargetDir); err != nil {
		return nil, err
	}

	return newPaths, nil
}
