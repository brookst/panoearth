#!/usr/bin/env python
"""Generate Google Earth placemarks in a panorama.
Ported from PHP https://gist.github.com/mavisland/9283594
"""

from __future__ import print_function
from math import pi, sin, cos, atan, sqrt, radians, degrees
from sys import stdout

class Pano(object):
    """Generate a panorama in Google Earth"""
    _lat = 0
    _lon = 0
    def __init__(self, lat, lon, alt, output=stdout):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.output = output
    @property
    def lat(self):
        return self._lat
    @lat.setter
    def lat(self, value):
        if isinstance(value, list):
            self._lat = value[0] + value[1]/60.0 + value[2]/3600.0
        else:
            self._lat = value

    @property
    def lon(self):
        return self._lon
    @lon.setter
    def lon(self, value):
        if isinstance(value, list):
            self._lon = value[0] + value[1]/60.0 + value[2]/3600.0
        else:
            self._lon = value

    def write(self):
        """Write Google Earth XML to output"""
        f = self.alt / 4000.0
        circles = [(0, 1),
                   (f * 2.5, 6),
                   (f * 5.0, 10),
                   (f * 10., 12),
                   (f * 50., 12),
                  ]
        self.write_header()
        for i in range(5):
            self.write_circle(circles[i])
        self.write_footer()

    def _write(self, data):
        """Internal"""
        print(data, file=self.output)

    def write_header(self):
        """Head block of Google Earth XML"""
        write = self._write
        write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        write("<kml xmlns=\"http://earth.google.com/kml/2.1\">")
        write("<Folder>")
        write("  <name>Panorama</name>")
        write("  <open>1</open>")

    def write_footer(self):
        """Tail block of Google Earth XML"""
        write = self._write
        write("</Folder>")
        write("</kml>")

    def write_point(self, num, rayon, angle):
        """Generate a placemark with a specified attitude"""
        d_lat = (rayon * cos(angle)) * (90. / 10000.)
        d_lon = (rayon * sin(angle)) * (90. / (10000 * cos(radians(self.lat))))

        lat = self._lat + d_lat
        lon = self._lon + d_lon
        alt = self.alt

        dist = sqrt(rayon * rayon * 1000. * 1000. + alt * alt)
        tilt = degrees(atan(rayon * 1000. / alt))
        heading = degrees(angle)

        write = self._write
        write("  <Placemark>")
        write("    <name>Position %02d</name>" % num)
        write("    <LookAt>")
        write("      <longitude>%f</longitude>" % lon)
        write("      <latitude>%f</latitude>" % lat)
        write("      <altitude>0</altitude>")
        write("      <range>%f</range>" % dist)
        write("      <tilt>%f</tilt>" % tilt)
        write("      <heading>%f</heading>" % heading)
        write("      <altitudeMode>absolute</altitudeMode>")
        write("    </LookAt>")
        write("  </Placemark>")

    def write_circle(self, args):
        """Generate a ring of attitudes at constant pitch"""
        rayon, num = args
        write = self._write
        write("<Folder>")
        write("  <name>Ring %3.1f</name>" % rayon)
        write("  <open>1</open>")

        for i in range(num):
            angle = i * 2 * pi / num
            self.write_point(i + 1, rayon, angle)

        write("</Folder>")


def get_args():
    """Command line arguments"""
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    add = parser.add_argument
    req = parser.add_argument_group('required arguments').add_argument
    req("-m", "--lat", type=float, required=True, help="latitude in degrees")
    req("-a", "--alt", type=float, required=True, help="altitude in meters")
    req("-p", "--lon", type=float, required=True, help="longitude in degrees")
    add("-f", "--file", type=str, metavar="NAME",
        help="output filename, e.g. pano.kml - "
             "print to stdout if not specified")
    return parser.parse_args()

def main():
    """Run from command line"""
    args = get_args()
    kml = open(args.file, "w") if args.file else stdout
    Pano(args.lat, args.lon, args.alt, kml).write()

if __name__ == '__main__':
    main()
