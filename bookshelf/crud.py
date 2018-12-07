# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from bookshelf import get_model, storage
from flask import Blueprint, current_app, redirect, render_template, request, \
    url_for


crud = Blueprint('crud', __name__)


# [START upload_image_file]
def upload_image_file(file):
    """
    Upload the user-uploaded file to Google Cloud Storage and retrieve its
    publicly-accessible URL.
    """
    if not file:
        return None

    public_url = storage.upload_file(
        file.read(),
        file.filename,
        file.content_type
    )

    current_app.logger.info(
        "Uploaded file %s as %s.", file.filename, public_url)

    return public_url
# [END upload_image_file]


@crud.route("/hotel")
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    hotels, next_page_token = get_model().hotelList(cursor=token)

    return render_template(
        "list.html",
        hotels=hotels,
        next_page_token=next_page_token)


@crud.route('/hotel/<id>')
def view(id):
    hotel = get_model().hotelRead(id)
    return render_template("view.html", hotel=hotel)


@crud.route('/hotel/add', methods=['GET', 'POST'])
def hotelAdd():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        # If an image was uploaded, update the data to point to the new image.
        # [START image_url]
        image_url = upload_image_file(request.files.get('image'))
        # [END image_url]

        # [START image_url2]
        if image_url:
            data['imageUrl'] = image_url
        # [END image_url2]

        hotel = get_model().hotelCreate(data)

        return redirect(url_for('.view', id=hotel['id']))

    return render_template("form.html", action="Add", hotel={})


@crud.route('/customer/add', methods=['GET', 'POST'])
def customerAdd():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True) # pulls data from formCostumer.html to dictionary datatype

        # If an image was uploaded, update the data to point to the new image.
        # [START image_url]
        image_url = upload_image_file(request.files.get('image'))
        # [END image_url]

        # [START image_url2]
        if image_url:
            data['imageUrl'] = image_url # if image supplied, add to costumer object
        # [END image_url2]

        customer = get_model().customerCreate(data) #calls costumerCreate instance from m_cloudsql, costumer class also in m_cloudsql

        return redirect(url_for('.view', id=customer['id']))

    return render_template("formCostumer.html", action="Add", customer={}) # passed to formCostumer.html


@crud.route('/hotel/<id>/edit', methods=['GET', 'POST'])
def hotelEdit(id):
    hotel = get_model().read(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        image_url = upload_image_file(request.files.get('image'))

        if image_url:
            data['imageUrl'] = image_url

        hotel = get_model().hotelUpdate(data, id)

        return redirect(url_for('.view', id=hotel['id']))

    return render_template("form.html", action="Edit", hotel=hotel)

@crud.route('/customer/<id>/edit', methods=['GET', 'POST'])
def customerEdit(id):
    costumer = get_model().read(id)   #CHANGED HOTEL TO COSTUMER

    if request.method == 'POST':                
        data = request.form.to_dict(flat=True)  

        image_url = upload_image_file(request.files.get('image'))

        if image_url:
            data['imageUrl'] = image_url

        costumer = get_model().customerUpdate(data, id)  #passed to m_cloudsql of costumer object and id, retrieves from db abd assigns to costumer
        #HOTEL TO COSTUMER ABOVE CHANGED
        return redirect(url_for('.view', id=customer['id'])) #??

    return render_template("Costumerform.html", action="Edit", customer=customer)   #calls template with action edit, and costumer object also passed
                        #CHANGED FORM TO COSTUMER FORM

@crud.route('/hotel/<id>/delete')
def hotelDelete(id):
    get_model().hotelDelete(id)
    return redirect(url_for('.list'))

@crud.route('/customer/<id>/delete')
def customerDelete(id):
    get_model().customerDelete(id)
    return redirect(url_for('.list'))
