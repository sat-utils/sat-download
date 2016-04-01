class RemoteFileDoesntExist(Exception):
    """ Exception to be used when the remote file does not exist """
    pass


class IncorrectLandsat8SceneId(Exception):
    """ Exception to be used when Landsat 8 scene id is incorrect """
    pass


class USGSInventoryAccessMissing(Exception):
    """ Exception for when User does not have access to USGS Inventory Service """
    pass
