# -*- coding: utf-8 -*-

from flask import request, url_for

def current_url(save_get_params=False, **updates):
     args = request.view_args.copy()
     args.update(updates)
     if save_get_params:
         args.update(request.args)
     return url_for(request.endpoint, **args)
