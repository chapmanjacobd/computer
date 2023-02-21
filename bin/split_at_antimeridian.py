"""
The following QGIS tool corrects polygons that are overlapping the
antimeridian by creating multipolygons with two parts on both sides
of the antimeridian.

Limitations:
- The geometry must be WGS 84 (EPSG:4326).
- Polygons must not have holes.

Dependencies:
- QGIS 3.22+ and PyQGIS
- shapely

Author:
Thomas Zuberbuehler (developed on private time for a Dal researcher/student)


Copyright (c) 2022 Thomas Zuberbuehler / Dalhousie University

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

Additional Disclaimer:

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

__author__ = "Thomas Zuberbuehler"
__date__ = "March 2022"
__copyright__ = "(c) 2022 Thomas Zuberbuehler / Dalhousie University"

import re

from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import (
    QgsGeometry,
    QgsPointXY,
    QgsVectorLayer,
    QgsProcessing,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterString,
    QgsProcessingAlgorithm,
    QgsFeature,
    QgsProcessingParameterFeatureSink,
    QgsFeatureSink,
)

from shapely import wkt
from shapely.geometry import Polygon, MultiPolygon

from qgis import processing
from qgis.core.additions.edit import edit

from typing import List


ANTI_MERIDIAN = QgsGeometry.fromPolylineXY([
    QgsPointXY(180, 90),
    QgsPointXY(180, -90),
]).buffer(0.0000001, 0)


def _pre_transform(x):
    if x < 0:
        return x + 180 + 180
    return x


def _post_transform(x):
    if x > 180:
        return x - 180 - 180
    return x


def update_geometry(geom: Polygon, transform_x) -> QgsGeometry:

    exterior = []
    for coord in geom.exterior.coords:
        x, y = transform_x(coord[0]), coord[1]
        exterior.append((x, y))
    
    interiors = []
    for i, interior in enumerate(geom.interiors):
        interiors.append([])
        for coord in interior.coords:
            x, y = transform_x(coord[0]), coord[1]
            interiors[i].append((x, y))
    
    return Polygon(exterior, interiors)
    

def load_wkt(wkt_string):
    
    try:

        return wkt.loads(wkt_string)

    except:

        match = re.search("Polygon[ ]?[(][(](?P<first_point>[0-9. -e]+?)[,]", wkt_string)
        first_point = match.group("first_point")
        wkt_string = f"{wkt_string[:-2]}, {first_point}))" 

        return wkt.loads(wkt_string)


def adjust_geometries(geom, feedback):
    
    wkt_string = geom.asWkt()  # using shapely objects, qgs objects are hell
    geom = load_wkt(wkt_string)
    
    if isinstance(geom, MultiPolygon):
        
        polygons = []
        
        for polygon in geom.geoms:
            updated_polygon = update_geometry(polygon, _pre_transform)
            polygons.append(updated_polygon)
        
        return QgsGeometry.fromWkt(MultiPolygon(polygons).wkt)

    return QgsGeometry.fromWkt(update_geometry(geom, _pre_transform).wkt)


def separate_geometries(geom):
    
    wkt_string = geom.asWkt()  # using shapely objects, qgs objects are hell
    geom = load_wkt(wkt_string)
    
    if isinstance(geom, MultiPolygon):
        
        polygons = []
        
        for polygon in geom.geoms:
            updated_polygon = update_geometry(polygon, _post_transform)
            polygons.append(updated_polygon)
        
        return QgsGeometry.fromWkt(MultiPolygon(polygons).wkt)

    return QgsGeometry.fromWkt(geom.wkt)


def correct_geometries(layer, control_meridians, context, feedback): 

    meridians = [
        QgsGeometry.fromPolylineXY([
            QgsPointXY(m, 90),
            QgsPointXY(m, -90),
        ])
        for m in control_meridians
    ]
    
    feedback.pushInfo("Create working layer...")

    result_layer = QgsVectorLayer("Polygon?crs=epsg:4326", "Corrected", "memory")
    features = [feature for feature in layer.getFeatures()]
    data_provider = result_layer.dataProvider()
    attributes = layer.dataProvider().fields().toList()
    data_provider.addAttributes(attributes)
    result_layer.updateFields()
    data_provider.addFeatures(features)
    
    feedback.pushInfo("Correct geometries...")

    modified = []
    
    with edit(result_layer):
        
        for feature in result_layer.getFeatures():
            
            geom = feature.geometry()
            
            is_candidate = all([
                geom.crosses(m) for m in meridians
            ])

            if is_candidate:

                modified.append(feature.id())

                geom = adjust_geometries(geom, feedback)
                result_layer.changeGeometry(feature.id(), geom)

    feedback.pushInfo("Split geometries...")
    
    overlay_layer = QgsVectorLayer("Polygon?crs=epsg:4326", "Overlay", "memory")
    overlay_data_provider = overlay_layer.dataProvider()
    overlay_feature = QgsFeature()
    overlay_feature.setGeometry(ANTI_MERIDIAN)
    overlay_data_provider.addFeatures([overlay_feature])
    overlay_layer.updateExtents()
    
    result = processing.run(
        "native:difference",
        {
            "INPUT": result_layer,
            "OVERLAY": overlay_layer,
            "OUTPUT": "memory:splitted"
        },
        context=context,
        feedback=feedback,
    )
    
    result_layer = result['OUTPUT']
    
    feedback.pushInfo("Separate geometries...")
    
    with edit(result_layer):
        
        for feature in result_layer.getFeatures():
            
            if feature.id() not in modified:
                continue
            
            geom = feature.geometry()
            
            geom = separate_geometries(geom)
            result_layer.changeGeometry(feature.id(), geom)

    return result_layer


class CalculateDistance(QgsProcessingAlgorithm):
    
    LAYER = "LAYER"
    CONTROL_MERIDIANS = "CONTROL_MERIDIANS"
    OUTPUT = "OUTPUT"

    def __init__(self):
        super().__init__()

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def name(self):
        return "CorrectGeometriesOverlappingAntiMeridian"
    
    def displayName(self):
        return "Correct geometries overlapping antimeridian"
    
    def group(self):
        return "Dal Tools"
    
    def groupId(self):
        return "dal-tools"
        
    def createInstance(self):
        return type(self)()

    def initAlgorithm(self, config=None):
        
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.LAYER, 
                self.tr("Layer"),
                [QgsProcessing.TypeVectorPolygon],
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.CONTROL_MERIDIANS,
                self.tr("Control Meridians"),
                defaultValue="-100,0,100",
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("Output Layer"),
            )
        )
    
    def processAlgorithm(self, parameters, context, feedback):

        input_layer = self.parameterAsVectorLayer(parameters, self.LAYER, context)

        control_meridians = [
            float(m) for m in self.parameterAsString(
                parameters,
                self.CONTROL_MERIDIANS,
                context
            ).split(",")
        ]

        result_layer = correct_geometries(
            input_layer, 
            control_meridians,
            context,
            feedback,
        )
        
        fields = input_layer.fields()
        (sink, sink_destination_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            input_layer.wkbType(),
            input_layer.sourceCrs(),
        )
        
        feedback.pushInfo("Prepare Output ...")
        
        for f in result_layer.getFeatures():

            feature = QgsFeature()
            feature.setGeometry(f.geometry())
            feature.setAttributes(f.attributes())
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

        return {self.OUTPUT: sink_destination_id}
