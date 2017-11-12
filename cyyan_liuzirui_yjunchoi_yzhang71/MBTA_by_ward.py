from collections import Counter
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import matplotlib.path as mplPath
import numpy as np
import pandas as pd

class MBTA_by_ward(dml.Algorithm):
    contributor = 'cyyan_liuzirui_yjunchoi_yzhang71'
    reads = ['cyyan_liuzirui_yjunchoi_yzhang71.boston_wards', 'cyyan_liuzirui_yjunchoi_yzhang71.MBTACoordinates']
    writes = ['cyyan_liuzirui_yjunchoi_yzhang71.MBTA_by_ward']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('cyyan_liuzirui_yjunchoi_yzhang71','cyyan_liuzirui_yjunchoi_yzhang71')

        # loads ward coordinate
        raw_ward = repo['cyyan_liuzirui_yjunchoi_yzhang71.boston_wards'].find({})

        # loads MBTA data
        raw_MBTA = repo['cyyan_liuzirui_yjunchoi_yzhang71.MBTACoordinates'].find({})

        # Collection ward coordinate
        path = {}
        for i in raw_ward:
            if isinstance(i['coordinates'][0][0], list):
                path[i['ward_num']] = mplPath.Path(i['coordinates'][0])
            else:
                path[i['ward_num']] = mplPath.Path(i['coordinates'])

        MBTA = []
        for i in raw_MBTA:
            for j in i['stations']:
                coordinates = []
                coordinates.append(j['longitude'])
                coordinates.append(j['latitude'])
                MBTA.append(coordinates)

        raw_ward = repo['cyyan_liuzirui_yjunchoi_yzhang71.boston_wards'].find({})

        MBTAByWard = {}
        for j in raw_ward:
            coordinate = []
            for i in range(len(MBTA)):
                if path[j['ward_num']].contains_point(MBTA[i]):
                    coordinate.append(MBTA[i])
            MBTAByWard[str(j['ward_num'])] = coordinate

        results = [MBTAByWard]
        # drop collection
        repo.dropCollection('MBTA_by_ward')
        # create collection
        repo.createCollection('MBTA_by_ward')
        # insert data in collection
        repo['cyyan_liuzirui_yjunchoi_yzhang71.MBTA_by_ward'].insert(results)

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}

    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('cyyan_liuzirui_yjunchoi_yzhang71','cyyan_liuzirui_yjunchoi_yzhang71')

        #create document object and define namespaces
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'http://datamechanics.io/data/yjunchoi_yzhang71/')
        doc.add_namespace('eri', 'http://erikdemaine.org/maps/mbta')

        #define entity to represent resources
        this_script = doc.agent('alg:cyyan_liuzirui_yjunchoi_yzhang71#MBTA_by_ward', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource1 = doc.entity('bdp:cyyan_liuzirui_yjunchoi_yzhang71#boston_wards', {prov.model.PROV_LABEL:'boston_wards', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'geojson'})
        resource2 = doc.entity('eri:cyyan_liuzirui_yjunchoi_yzhang71#MBTACoordinates', {prov.model.PROV_LABEL:'MBTACoordinates', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'yaml'})

        run_MBTA_by_ward = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(run_MBTA_by_ward, this_script)

        doc.usage(run_MBTA_by_ward, resource1, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation',})
        doc.usage(run_MBTA_by_ward, resource2, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Computation',})

        p = doc.entity('dat:cyyan_liuzirui_yjunchoi_yzhang71#boston_wards', {prov.model.PROV_LABEL:'boston_wards', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(p, this_script)
        doc.wasGeneratedBy(p, run_MBTA_by_ward, endTime)
        doc.wasDerivedFrom(p, resource1, run_MBTA_by_ward, run_MBTA_by_ward, run_MBTA_by_ward)

        h = doc.entity('dat:cyyan_liuzirui_yjunchoi_yzhang71#MBTACoordinates', {prov.model.PROV_LABEL:'MBTACoordinatess', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(h, this_script)
        doc.wasGeneratedBy(h, run_MBTA_by_ward, endTime)
        doc.wasDerivedFrom(h, resource2, run_MBTA_by_ward, run_MBTA_by_ward, run_MBTA_by_ward)

        repo.logout()

        return doc

# MBTA_by_ward.execute()
# doc = MBTA_by_ward.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
#
# ## eof
