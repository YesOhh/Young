#!/usr/bin/python
# -*- coding: UTF-8 -*-
# ===========================================================
#      Author : yxu
#       Email :
#        Date : 
# Description : 
#        Args : 
# ===========================================================

from flask import (
    request,
    redirect,
    url_for,
    current_app
)
from urllib.parse import (
    urlparse,
    urljoin,
    urlencode
)
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import (
    SignatureExpired,
    BadSignature
)
from young.settings import Operation
from young.extensions import db
from young.models import User


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='main.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def generate_token(user, operation, expire_in=None, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expire_in)
    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)


def validate_token(user, token, operation, new_password=None):
    s = Serializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if operation != data.get('operation') or user.id != data.get('id'):
        return False

    if operation == Operation.CONFIRM:
        user.confirmed = True
    elif operation == Operation.RESET_PASSWORD:
        user.set_password(new_password)
    elif operation == Operation.CHANGE_EMAIL:
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if User.query.filter_by(email=new_email).first() is not None:
            return False
        user.email = new_email
    else:
        return False

    db.session.commit()
    return True


class SelfPagination(object):
    """
    自定义分页
    """

    def __init__(self, current_page, total_count, base_url, params, per_page_count=10, max_pager_count=11):
        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1
        if current_page <= 0:
            current_page = 1
        self.current_page = current_page
        # 数据总条数
        self.total_count = total_count

        # 每页显示10条数据
        self.per_page_count = per_page_count

        # 页面上应该显示的最大页码
        max_page_num, div = divmod(total_count, per_page_count)
        if div:
            max_page_num += 1
        self.max_page_num = max_page_num

        # 页面上默认显示11个页码（当前页在中间）
        self.max_pager_count = max_pager_count
        self.half_max_pager_count = int((max_pager_count - 1) / 2)

        # URL前缀
        self.base_url = base_url

        # request.GET
        import copy
        params = copy.deepcopy(params)
        get_dict = params.to_dict()

        self.params = get_dict

    @property
    def start(self):
        return (self.current_page - 1) * self.per_page_count

    @property
    def end(self):
        return self.current_page * self.per_page_count

    def page_html(self):
        # 如果总页数 <= 11
        if self.max_page_num <= self.max_pager_count:
            pager_start = 1
            pager_end = self.max_page_num
        # 如果总页数 > 11
        else:
            # 如果当前页 <= 5
            if self.current_page <= self.half_max_pager_count:
                pager_start = 1
                pager_end = self.max_pager_count
            else:
                # 当前页 + 5 > 总页码
                if (self.current_page + self.half_max_pager_count) > self.max_page_num:
                    pager_end = self.max_page_num
                    pager_start = self.max_page_num - self.max_pager_count + 1  # 倒这数11个
                else:
                    pager_start = self.current_page - self.half_max_pager_count
                    pager_end = self.current_page + self.half_max_pager_count

        page_html_list = []
        # 首页
        self.params['page'] = 1
        if self.current_page != 1:
            first_page = '<li class="page-item"><a class="page-link text-secondary" href="%s?%s">&laquo;</a></li>' % (self.base_url, urlencode(self.params),)
        else:
            first_page = '<li class="page-item disabled"><a class="page-link text-secondary" href="%s?%s">&laquo;</a></li>' % (self.base_url, urlencode(self.params),)
        page_html_list.append(first_page)
        # 上一页
        # self.params["page"] = self.current_page - 1
        # if self.params["page"] < 1:
        #     pervious_page = '<li class="disabled"><a href="%s?%s" aria-label="Previous">上一页</span></a></li>' % (
        #     self.base_url, urlencode(self.params))
        # else:
        #     pervious_page = '<li><a href = "%s?%s" aria-label = "Previous" >上一页</span></a></li>' % (
        #         self.base_url, urlencode(self.params))
        # page_html_list.append(pervious_page)
        # 中间页码
        for i in range(pager_start, pager_end + 1):
            self.params['page'] = i
            if i == self.current_page:
                temp = '<li class="page-item active"><a class="page-link" href="#">%s <span class="sr-only">(current)</span></a></li>' % (i,)
            else:
                temp = '<li class="page-item"><a class="page-link" href="%s?%s">%s</a></li>' % (self.base_url, urlencode(self.params), i,)
            page_html_list.append(temp)

        # 下一页
        # self.params["page"] = self.current_page + 1
        # if self.params["page"] > self.max_page_num:
        #     self.params["page"] = self.current_page
        #     next_page = '<li class="disabled"><a href = "%s?%s" aria-label = "Next">下一页</span></a></li >' % (
        #     self.base_url, urlencode(self.params))
        # else:
        #     next_page = '<li><a href = "%s?%s" aria-label = "Next">下一页</span></a></li>' % (
        #         self.base_url, urlencode(self.params))
        # page_html_list.append(next_page)

        # 尾页
        self.params['page'] = self.max_page_num
        if self.current_page != self.max_page_num:
            last_page = '<li class="page-item"><a class="page-link text-secondary" href="%s?%s">&raquo;</a></li>' % (self.base_url, urlencode(self.params),)
        else:
            last_page = '<li class="page-item disabled"><a class="page-link text-secondary" href="%s?%s">&raquo;</a></li>' % (self.base_url, urlencode(self.params),)
        page_html_list.append(last_page)

        return ''.join(page_html_list)
