package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestCollapseLayers(t *testing.T) {
	tmpDir, err := os.MkdirTemp("", "collapse_test_*")
	if err != nil {
		t.Fatalf("failed to create temp dir: %v", err)
	}
	defer os.RemoveAll(tmpDir)

	parent := filepath.Join(tmpDir, "src")
	target := filepath.Join(parent, "match_me")
	childDir := filepath.Join(target, "subfolder")

	if err := os.MkdirAll(childDir, 0755); err != nil {
		t.Fatalf("failed to create setup dirs: %v", err)
	}

	file1 := filepath.Join(target, "file1.txt")
	file2 := filepath.Join(childDir, "file2.txt")

	if err := os.WriteFile(file1, []byte("data1"), 0644); err != nil {
		t.Fatalf("failed to write file1: %v", err)
	}
	if err := os.WriteFile(file2, []byte("data2"), 0644); err != nil {
		t.Fatalf("failed to write file2: %v", err)
	}

	args := MoveArgs{
		Root:    parent,
		Targets: map[string]bool{"match_me": true},
	}

	if err := collapseLayers(args); err != nil {
		t.Fatalf("collapseLayers failed: %v", err)
	}

	expectedFile1 := filepath.Join(parent, "file1.txt")
	expectedSubfolder := filepath.Join(parent, "subfolder")
	expectedFile2 := filepath.Join(expectedSubfolder, "file2.txt")

	if _, err := os.Stat(expectedFile1); os.IsNotExist(err) {
		t.Errorf("expected file1 to be lifted to %s, but it does not exist", expectedFile1)
	}

	if _, err := os.Stat(expectedFile2); os.IsNotExist(err) {
		t.Errorf("expected nested file2 to exist at %s, but it does not exist", expectedFile2)
	}

	if _, err := os.Stat(target); !os.IsNotExist(err) {
		t.Errorf("expected target directory %s to be deleted, but it still exists", target)
	}
}

func TestCollapseLayers_MultipleScenarios(t *testing.T) {
	tests := []struct {
		name       string
		targets    map[string]bool
		setupDirs  []string
		setupFiles []string
		wantExist  []string
		wantAbsent []string
	}{
		{
			name:    "Single layer matching folder is lifted",
			targets: map[string]bool{"drop": true},
			setupDirs: []string{
				"root/drop",
				"root/keep",
			},
			setupFiles: []string{
				"root/drop/a.txt",
				"root/keep/b.txt",
			},
			wantExist: []string{
				"root/a.txt",
				"root/keep/b.txt",
			},
			wantAbsent: []string{
				"root/drop",
			},
		},
		{
			name:    "Consecutive nested matching targets",
			targets: map[string]bool{"drop": true},
			setupDirs: []string{
				"root/drop",
				"root/drop/drop",
			},
			setupFiles: []string{
				"root/drop/drop/deep.txt",
			},
			wantExist: []string{
				"root/deep.txt",
			},
			wantAbsent: []string{
				"root/drop",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tmpDir, err := os.MkdirTemp("", "collapse_multi_*")
			if err != nil {
				t.Fatalf("failed to create temp dir: %v", err)
			}
			defer os.RemoveAll(tmpDir)

			for _, d := range tt.setupDirs {
				os.MkdirAll(filepath.Join(tmpDir, d), 0755)
			}
			for _, f := range tt.setupFiles {
				os.WriteFile(filepath.Join(tmpDir, f), []byte("test"), 0644)
			}

			args := MoveArgs{
				Root:    filepath.Join(tmpDir, "root"),
				Targets: tt.targets,
			}

			_ = collapseLayers(args)

			for _, path := range tt.wantExist {
				full := filepath.Join(tmpDir, path)
				if _, err := os.Stat(full); os.IsNotExist(err) {
					t.Errorf("expected path to exist: %s", path)
				}
			}

			for _, path := range tt.wantAbsent {
				full := filepath.Join(tmpDir, path)
				if _, err := os.Stat(full); !os.IsNotExist(err) {
					t.Errorf("expected path to be removed: %s", path)
				}
			}
		})
	}
}
