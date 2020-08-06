# Complex orthanc functions to consider

def rfind(self, query, domain, retrieve=False):
    # logger = logging.getLogger(name=self.name)
    # logger.debug(pformat(query))

    result = []

    resource = "modalities/{}/query".format(domain)
    response0 = self._post(resource, json=query)
    # logger.debug(response0)

    if response0.get('ID'):
        resource = "queries/{}/answers".format(response0.get('ID'))
        response1 = self._get(resource)
        # logger.debug(response1)

        for answer in response1:
            # logger.debug(answer)
            resource = "queries/{}/answers/{}/content?simplify".format(response0.get('ID'), answer)
            response2 = self._get(resource)
            result.append(response2)
            # logger.debug(response2)

            if retrieve:
                resource = "queries/{}/answers/{}/retrieve".format(response0.get('ID'), answer)
                response3 = self._post(resource, data=self.aet)
                result.append(response3)
                # logger.debug(response3)

    return result


def get(self, oid: str, level: DicomLevel, view: str="tags"):

    if view == "tags":
        if level == DicomLevel.INSTANCES:
            resource = "{!s}/{}/tags?simplify".format(level, oid)
        else:
            resource = "{!s}/{}/shared-tags?simplify".format(level, oid)
    elif view == "meta":
        resource = "{!s}/{}".format(level, oid)
    elif view == "metakv":
        r = {}
        for k in orthanc_metadata_keys:
            try:
                v = self.get_metadata(oid, level, k)
            except GatewayConnectionError:
                v = None
            r[k] = v
        return r

    elif view == "file":
        if level == DicomLevel.INSTANCES:
            resource = "{!s}/{}/file".format(level, oid)
        else:
            resource = "{!s}/{}/archive".format(level, oid)
    else:
        raise TypeError("Unknown view requested")

    return self._get(resource)


