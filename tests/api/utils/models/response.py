import json
from cafe.engine.models import base


class CreateService(base.AutoMarshallingModel):
    """
    Marshalling for Create Service requests
    """

    def __init__(self, domain_list=None, origin_list=None, caching_list=None):
        super(CreateService, self).__init__()

        self.domain_list = domain_list or []
        self.origin_list = origin_list or []
        self.caching_list = caching_list or []

    def _obj_to_json(self):
        create_service_request = {"domains": self.domain_list,
                                  "origins": self.origin_list,
                                  "caching": self.caching_list}
        return json.dumps(create_service_request)
