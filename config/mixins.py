from django.http import JsonResponse
from django.template.loader import render_to_string


class LoadMoreMixin:
    item_template = None

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.render_json(context)
        return super().render_to_response(context, **response_kwargs)

    def render_json(self, context):
        page_obj = context['page_obj']
        object_list = context['object_list']

        html = render_to_string(self.item_template, {
            'items': object_list,
            'request': self.request,
        })

        next_url = ''
        if page_obj.has_next():
            next_url = f'?page={page_obj.next_page_number()}'

        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
            'next_url': next_url,
        })
