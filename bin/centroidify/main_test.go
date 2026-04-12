package main

import (
	"encoding/json"
	"testing"

	"github.com/twpayne/go-geos"
)

func TestRepresentativePoint(t *testing.T) {
	ctx := geos.NewContext()

	tests := []struct {
		name         string
		geojson      string
		expectedType geos.TypeID
		expectIsPt   bool
	}{
		{
			name:         "Point",
			geojson:      `{"type": "Point", "coordinates": [10, 20]}`,
			expectedType: geos.TypeIDPoint,
			expectIsPt:   true,
		},
		{
			name:         "LineString",
			geojson:      `{"type": "LineString", "coordinates": [[0, 0], [10, 0]]}`,
			expectedType: geos.TypeIDPoint,
			expectIsPt:   false,
		},
		{
			name:         "MultiLineString",
			geojson:      `{"type": "MultiLineString", "coordinates": [[[0, 0], [10, 0]], [[0, 10], [5, 10]]]}`,
			expectedType: geos.TypeIDPoint,
			expectIsPt:   false,
		},
		{
			name:         "Polygon (centroid inside)",
			geojson:      `{"type": "Polygon", "coordinates": [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]}`,
			expectedType: geos.TypeIDPoint,
			expectIsPt:   false,
		},
		{
			name:         "Polygon (U-shape, centroid outside)",
			geojson:      `{"type": "Polygon", "coordinates": [[[0, 0], [0, 10], [10, 10], [10, 8], [2, 8], [2, 2], [10, 2], [10, 0], [0, 0]]]}`,
			expectedType: geos.TypeIDPoint,
			expectIsPt:   false,
		},
		{
			name:         "GeometryCollection",
			geojson:      `{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [10, 20]}]}`,
			expectedType: geos.TypeIDPoint,
			expectIsPt:   false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			g, err := ctx.NewGeomFromGeoJSON(tt.geojson)
			if err != nil {
				t.Fatalf("failed to parse geojson: %v", err)
			}

			pt, isPt, err := representativePoint(g, 1)
			if err != nil {
				t.Fatalf("representativePoint returned error: %v", err)
			}

			if pt.TypeID() != tt.expectedType {
				t.Errorf("expected type %v, got %v", tt.expectedType, pt.TypeID())
			}
			if isPt != tt.expectIsPt {
				t.Errorf("expected isPoint=%v, got %v", tt.expectIsPt, isPt)
			}
		})
	}
}

func TestIsNullJSON(t *testing.T) {
	if !isNullJSON(json.RawMessage("null")) {
		t.Error("expected true for 'null'")
	}
	if !isNullJSON(json.RawMessage("")) {
		t.Error("expected true for empty")
	}
	if isNullJSON(json.RawMessage(`{"type":"Point"}`)) {
		t.Error("expected false for object")
	}
}
