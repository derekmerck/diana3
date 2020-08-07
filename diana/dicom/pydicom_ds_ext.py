"""
PyDicom Dataset Extensions

Derek Merck, Spring 2020

Provides "get_dict" method that recursively generates a
standard python k,v dictionary from dataset tags, comparable to
the simplified header produced by Orthanc, for example.

Provides "get_pixels(dtype)" method that returns appropriately
shaped, scaled, and offset uint16, int16 (hounsfield), or uint8
values as a new Numpy array.
"""

import logging
import pydicom
import numpy as np
from libsvc.utils import ExceptionHandlingIterator


def get_dict(ds: pydicom.Dataset) -> dict:
    output = dict()

    _ds = ExceptionHandlingIterator(ds)
    # Wrap iterator in code to discard exceptions

    def get_value(item):
        if type(item) == pydicom.valuerep.DSfloat:
            return float(item)
        elif type(item) == pydicom.valuerep.IS:
            return int(item)
        elif type(item) == pydicom.uid.UID:
            return str(item)
        elif hasattr(item, "value"):
            return get_value(item.value)
        else:
            return item

    for elem in _ds:
        if elem.keyword == "PixelData":
            continue
            # Deal with that separately
        elif not elem.value or not elem.keyword:
            continue
        elif elem.VR == "PN":
            output[elem.keyword] = str(elem.value)
        elif elem.VM != 1 and elem.VR == 'SQ':
            # elif elem.keyword == "AdmittingDiagnosesCodeSequence":
            #     print(f"Diagnosis Code: VM {elem.VM} VR {elem.VR}")
            output[elem.keyword] = [get_dict(item) for item in elem]
        elif elem.VM != 1:
            # print(f"VM ne 1: VM {elem.VM} VR {elem.VR}")
            output[elem.keyword] = [get_value(item) for item in elem]
        elif elem.VR != 'SQ':
            output[elem.keyword] = get_value(elem.value)


        else:
            output[elem.keyword] = [get_dict(item) for item in elem]

    # MONOCHROME, RGB etc.
    if (0x0028, 0x0004) in ds:
        output['PhotometricInterpretation'] = ds[0x0028, 0x0004].value

    return output


def get_pixels(ds: pydicom.Dataset, units="uint8"):

    if ds.pixel_array is None:
        raise TypeError("No pixel data available")

    if ds.get('PhotometricInterpretation') == "RGB":
        pixels = ds.pixel_array.reshape([ds.get("Rows"),
                                        ds.get("Columns"),
                                        3])
    else:
        pixels = ds.pixel_array

    # No processing required, return values 0-4096 as uint16
    if units == "uint16":
        if pixels.dtype != "uint16":
            pixels = np.uint16(pixels)
        return pixels

    # Convert to HU, this is computed from header info, but
    # practically, it is always (pixels - 1024) * 1
    elif units == "int16":
        if ds.get("RescaleSlope") and \
                ds.get("RescaleIntercept"):
            if pixels.dtype == "uint16":
                pixels = np.int16(pixels)
            pixels *= int(ds.get("RescaleSlope"))
            pixels += int(ds.get("RescaleIntercept"))
        else:
            logging.debug("No rescale slope/intercept in DICOM header")

    # Covert to floats and cast to 8-bit
    elif units == "uint8":
        pixels = pixels.astype("float")
        pixels = ((pixels - pixels.min())) / (pixels.max() - pixels.min())
        pixels = pixels * 255
        pixels = pixels.astype("uint8")

    return pixels


# Monkey Patch
pydicom.Dataset.get_dict = get_dict
pydicom.Dataset.get_pixels = get_pixels
