package docker

import (
	"archive/tar"
	"bytes"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

// tarDirectoryFlat builds a tar archive of all regular files under root (recursive),
// with paths relative to root using slash separators (Docker expects POSIX names).
func tarDirectoryFlat(root string) (*tarBuffer, error) {
	root = filepath.Clean(root)
	buf := &tarBuffer{}
	tw := tar.NewWriter(buf)
	err := filepath.WalkDir(root, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() {
			return nil
		}
		rel, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		if rel == "." || strings.HasPrefix(rel, "..") {
			return nil
		}
		info, err := d.Info()
		if err != nil {
			return err
		}
		hdr, err := tar.FileInfoHeader(info, "")
		if err != nil {
			return err
		}
		hdr.Name = filepath.ToSlash(rel)
		if err := tw.WriteHeader(hdr); err != nil {
			return err
		}
		f, err := os.Open(path)
		if err != nil {
			return err
		}
		_, err = io.Copy(tw, f)
		_ = f.Close()
		return err
	})
	if err != nil {
		_ = tw.Close()
		return nil, err
	}
	if err := tw.Close(); err != nil {
		return nil, err
	}
	return buf, nil
}

type tarBuffer struct {
	b []byte
}

func (t *tarBuffer) Write(p []byte) (n int, err error) {
	t.b = append(t.b, p...)
	return len(p), nil
}

func tarDirectoryFlatReader(root string) (io.Reader, error) {
	tb, err := tarDirectoryFlat(root)
	if err != nil {
		return nil, err
	}
	return bytes.NewReader(tb.b), nil
}

func copyFileFromContainerTar(r io.Reader, destPath string) error {
	tr := tar.NewReader(r)
	hdr, err := tr.Next()
	if err != nil {
		return fmt.Errorf("empty or invalid tar from container: %w", err)
	}
	if hdr.Typeflag != tar.TypeReg && hdr.Typeflag != tar.TypeRegA {
		return fmt.Errorf("unexpected tar entry type %c", hdr.Typeflag)
	}
	out, err := os.OpenFile(destPath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0o755)
	if err != nil {
		return err
	}
	defer out.Close()
	if _, err := io.Copy(out, tr); err != nil {
		return err
	}
	return nil
}

// extractClassFilesFromTar reads a tar stream and writes every *.class into destDir.
func extractClassFilesFromTar(r io.Reader, destDir string) error {
	tr := tar.NewReader(r)
	for {
		hdr, err := tr.Next()
		if err == io.EOF {
			return nil
		}
		if err != nil {
			return err
		}
		if hdr.Typeflag != tar.TypeReg && hdr.Typeflag != tar.TypeRegA {
			continue
		}
		base := filepath.Base(hdr.Name)
		if !strings.HasSuffix(base, ".class") {
			continue
		}
		if strings.Contains(base, "..") {
			continue
		}
		path := filepath.Join(destDir, base)
		out, err := os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0o644)
		if err != nil {
			return err
		}
		_, err = io.Copy(out, tr)
		_ = out.Close()
		if err != nil {
			return err
		}
	}
}
