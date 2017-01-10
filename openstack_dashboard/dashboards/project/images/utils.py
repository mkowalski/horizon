# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions

from openstack_dashboard.api import glance


def get_available_images(request, project_id=None, images_cache=None):
    """Returns a list of images that are available in a certain context.
    Project_id is here only for backwards compatibility. The function shall return
    public, private and shared images.

    :param images_cache: An optional dict-like object in which to
    cache image metadata.

    """

    if images_cache is None:
        images_cache = {}

    all_images = images_cache.get('all_images', [])

    if 'all_images' not in images_cache:
        try:
            images, _more, _prev = glance.image_list_detailed(
                request)
            [all_images.append(image) for image in images]
            images_cache['all_images'] = images
        except Exception:
            exceptions.handle(request,
                              _("Unable to retrieve images."))

    return [image for image in all_images
            if image.container_format not in ('aki', 'ari')]


def image_field_data(request, include_empty_option=False):
    """Returns a list of tuples of all images.

    Generates a sorted list of images available. And returns a list of
    (id, name) tuples.

    :param request: django http request object
    :param include_empty_option: flag to include a empty tuple in the front of
        the list

    :return: list of (id, name) tuples

    """
    try:
        images = get_available_images(request, request.user.project_id)
    except Exception:
        exceptions.handle(request, _('Unable to retrieve images'))
    images.sort(key=lambda c: c.name)
    images_list = [('', _('Select Image'))]
    for image in images:
        image_label = u"{} ({})".format(image.name, filesizeformat(image.size))
        images_list.append((image.id, image_label))

    if not images:
        return [("", _("No images available")), ]

    return images_list
