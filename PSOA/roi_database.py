import numpy as np
from shapely.geometry import Polygon


# JUST as an example, some Europa regions are defined
def roi_database():

    # Entire dictionary of regions
    roilist = dict()

    # 'AMERGIN'
    roi = dict()
    roi['vertices'] = np.array([[125, -5], [125, -25], [135, -25], [135, -5]])
    roi['rgn_name'] = 'Amergin'
    roi['rgn_key'] = 'Amergin'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['AMERGIN'] = roi

    # 'AMERGIN_SOUTH'
    roi = dict()
    roi['vertices'] = np.array([[110, -30], [110, -15], [140, -15], [140, -30]])
    roi['rgn_name'] = 'Amergin South'
    roi['rgn_key'] = 'Amergin South'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['AMERGIN_SOUTH'] = roi

    # 'ANNWN_REGIO':
    roi = dict()
    roi['vertices'] = np.array([[50, 30], [50, 15], [30, 15], [30, 30]])
    roi['rgn_name'] = 'Annwn Regio'
    roi['rgn_key'] = 'Annwn Regio'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['ANNWN_REGIO'] = roi

    # 'BELUS_LINEA'
    roi = dict()
    roi['vertices'] = np.array([[120, 5], [120, 15], [135, 15], [135, 5]])
    roi['rgn_name'] = 'Belus Linea'
    roi['rgn_key'] = 'Belus Linea'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['BELUS_LINEA'] = roi

    # 'CILIX_CRATER': Deactivated until end-of-the-world issue is solved
    # roi = dict()
    # roi['vertices'] = np.array([[-177, 3], [-177, -3], [177, -3], [177, 3]])
    # roi['rgn_name'] = 'Cilix Crater'
    # roi['rgn_key'] = 'Cilix Crater'
    # roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    # roi['campaign'] = 'local'
    # roilist['CILIX_CRATER'] = roi

    # 'FALGA_REGIO'
    roi = dict()
    roi['vertices'] = np.array([[145, 35], [145, 25], [160, 25], [160, 35]])
    roi['rgn_name'] = 'Falga Regio'
    roi['rgn_key'] = 'Falga Regio'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['FALGA_REGIO'] = roi

    # 'HARMONIA_LINEA'
    roi = dict()
    roi['vertices'] = np.array([[-180, 20], [-180, 40], [-150, 40], [-150, 20]])
    roi['rgn_name'] = 'Harmonia Linea'
    roi['rgn_key'] = 'Harmonia Linea'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['HARMONIA_LINEA'] = roi

    # 'LUCHTAR'
    roi = dict()
    roi['vertices'] = np.array([[110, -35], [110, -50], [90, -50], [90, -35]])
    roi['rgn_name'] = 'Luchtar'
    roi['rgn_key'] = 'Luchtar'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['LUCHTAR'] = roi

    # 'MINOS_UDAEUS_LINEAE'
    roi = dict()
    roi['vertices'] = np.array([[135, 40], [135, 50], [150, 50], [150, 40]])
    roi['rgn_name'] = 'Minos-Udaeus Lineae'
    roi['rgn_key'] = 'Minos-Udaeus Lineae'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['MINOS_UDAEUS_LINEAE'] = roi

    # 'MOYLE_CAVUS'
    roi = dict()
    roi['vertices'] = np.array([[-180, -30], [-180, -15], [-160, -15], [-160, -30]])
    roi['rgn_name'] = 'Moyle Cavus'
    roi['rgn_key'] = 'Moyle Cavus'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['MOYLE_CAVUS'] = roi

    # 'MOYTURA_REGIO'
    roi = dict()
    roi['vertices'] = np.array([[50, -55], [50, -40], [80, -40], [80, -55]])
    roi['rgn_name'] = 'Moytura Regio'
    roi['rgn_key'] = 'Moytura Regio'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['MOYTURA_REGIO'] = roi

    # 'NIAMH':
    roi = dict()
    roi['vertices'] = np.array([[150, 25], [150, 15], [135, 15], [135, 25]])
    roi['rgn_name'] = 'Niamh'
    roi['rgn_key'] = 'Niamh'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['NIAMH'] = roi

    # TODO: FIX DUPLICATED NIAMH

    # 'NIAMH'
    roi = dict()
    roi['vertices'] = np.array([[55, 32], [55, -12], [92, -12], [92, 32]])
    roi['rgn_name'] = 'Niamh'
    roi['rgn_key'] = 'Niamh'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['NIAMH'] = roi

    # 'PWYLL_CRATER'
    roi = dict()
    roi['vertices'] = np.array([[105, -35], [105, -15], [75, -15], [75, -35]])
    roi['rgn_name'] = 'Pwyll Crater'
    roi['rgn_key'] = 'Pwyll Crater'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['PWYLL_CRATER'] = roi

    # 'PWYLL_CRATER_SOUTH'
    roi = dict()
    roi['vertices'] = np.array([[80, -55], [80, -75], [110, -75], [110, -55]])
    roi['rgn_name'] = 'Pwyll Crater South'
    roi['rgn_key'] = 'Pwyll Crater South'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['PWYLL_CRATER_SOUTH'] = roi

    # 'RHADAMANTHYS_LINEA'
    roi = dict()
    roi['vertices'] = np.array([[165, 20], [165, 10], [145, 10], [145, 20]])
    roi['rgn_name'] = 'Rhadamanthys Linea'
    roi['rgn_key'] = 'Rhadamanthys Linea'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['RHADAMANTHYS_LINEA'] = roi

    # 'TALIESIN'
    roi = dict()
    roi['vertices'] = np.array([[-150, -10], [-150, -30], [-125, -30], [-125, -10]])
    roi['rgn_name'] = 'Taliesin'
    roi['rgn_key'] = 'Taliesin'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['TALIESIN'] = roi

    # 'TARA_REGIO':
    roi = dict()
    roi['vertices'] = np.array([[-55, 20], [-85, 20], [-85, -20], [-55, -20]])
    roi['rgn_name'] = 'Tara Regio'
    roi['rgn_key'] = 'Tara Regio'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['TARA_REGIO'] = roi

    # 'TYRE'
    roi = dict()
    roi['vertices'] = np.array([[-130, 25], [-130, 45], [-160, 45], [-160, 25]])
    roi['rgn_name'] = 'Tyre'
    roi['rgn_key'] = 'Tyre'
    roi['centroid'] = Polygon(roi['vertices']).centroid.xy
    roi['campaign'] = 'local'
    roilist['TYRE'] = roi

    # Return entire dictionary
    return roilist

    # else:
    #    filename = arg
    #    with open(filename, 'r') as fid:
    #        out = [line.split(',') for line in fid.readlines() if not line.startswith('#')]
    #        for i in range(len(out)):
    #            roi['rgn_key'] = out[i][0].strip()
    #            roi['rgn_name'] = out[i][1].strip()
    #            roi['vertices'] = np.array([[float(out[i][3]), float(out[i][2])]])
    #            # Watch out for the longitude shift
    #            if roi['vertices'][0, 0] > 180:
    #                roi['vertices'][0, 0] -= 360
    #            x, y = amsplit(roi['vertices'][:, 0], roi['vertices'][:, 1])
    #            if np.isnan(x).any():
    #                cx, cy = centroid(Polygon(x, y), list(range(1, np.sum(np.isnan(x)) + 2)))
    #            else:
    #                cx, cy = centroid(Polygon(x, y))
    #            roi['cpoint'] = [cx, cy]
    #            roi['campaign'] = 'local'
    #            roilist.append(roi.copy())

# Define the remaining functions: amsplit, centroid
# Make sure to implement them in Python as well
