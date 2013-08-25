# -*- coding: utf-8 -*-
from functools import wraps

from flask import request, url_for, Response
from werkzeug.wrappers import BaseResponse

from librarian.models import Author, Book, Sequence


def current_url(save_get_params=False, **updates):
    kwargs = request.view_args.copy()
    if save_get_params:
        kwargs.update(request.args)
    kwargs.update(updates)
    return url_for(request.endpoint, **kwargs)


def books_sorted(query):
    return (
        query
        .order_by(Book.sequence_id)
        .order_by(Book.sequence_number)
    )


def authors_sorted(query):
    return (
        query
        .order_by(Author.last_name)
    )


def seqs_sorted(query):
    return (
        query
        .order_by(Sequence.title)
    )


def xml_response(endpoint):
    @wraps(endpoint)
    def wrapper(*args, **kwargs):
        result = endpoint(*args, **kwargs)
        # catch redirects, already response object.
        if isinstance(result, BaseResponse):
            return result
        return Response(result, mimetype='text/xml')
    return wrapper
