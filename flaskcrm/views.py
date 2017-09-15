from itertools import cycle
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm.collections import InstrumentedList
from flask_admin.model import typefmt
from jinja2 import Markup
from datetime import datetime
from models import db, TaskAssignment as TaskAssignmentModel, Telephone as TelephoneModel, Email as EmailModel, Contact as ContactModel, Company as CompanyModel, Organization as OrganizationModel, Deal as DealModel, Deal as DealModel, Link as LinkModel, Project as ProjectModel, Sprint as SprintModel, Task as TaskModel, Comment as CommentModel, Message as MessageModel
from flask_admin.base import expose


def format_instrumented_list(view, context, model, name):

    value = getattr(model, name)
    out = ""
    if isinstance(value, InstrumentedList):
        out = "<ul>"
        for x in value:
            if x is None:  # items can be created from empty forms in the form. let's fix that in the model
                continue
            if hasattr(x, "admin_view_link"):
                out += "<li><a href='{}'>{}</a></li>".format(
                    getattr(x, "admin_view_link")(), x)
            else:
                out += str(x)
        out += "</ul>"
    return Markup(out)


def format_url(view, context, model, name):
    value = getattr(model, name)
    return Markup("<a href='{url}'>{url}</a>".format(url=value))


def format_datetime(view, context, model, name):
    value = getattr(model, name)
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")


def format_comments(view, context, model, name):
    value = getattr(model, name)
    out = ""

    if isinstance(value, InstrumentedList):
        out = "<ul>"
        for x in value:
            if hasattr(x, "admin_view_link"):
                out += "<li>{commenttitle} {commentcontent}<a href='{commentadminlink}'> Read more...</a></li>".format(
                    commentadminlink=getattr(x, "admin_view_link")(), commenttitle=x.name, commentcontent=x.content)
            else:
                out += str(x)
        out += "</ul>"
    return Markup(out)


formatters = dict(list(zip(["telephones", "emails", "users", "contacts", "organizations", "projects",  "deals", "sprints",
                            "links", "tasks", "messages"], cycle([format_instrumented_list]))), comments=format_comments, url=format_url)

formatters = {**formatters, **
              dict(list(zip(["created_at", "updated_at", "closed_at", "start_date", "deadline", "eta"], cycle([format_datetime]))))}


class EnhancedModelView(ModelView):
    can_view_details = True
    column_formatters = formatters
    create_modal = True
    edit_modal = True

    mainfilter = ""

    form_widget_args = {
        'created_at': {
            'readonly': True,
        },
        'updated_at': {
            'readonly': True,
        },
    }

    def get_filter_arg_helper(self, filter_name, filter_op='equals'):
        filters = self._filter_groups[filter_name].filters
        position = list(self._filter_groups.keys()).index(filter_name)

        for f in filters:
            if f['operation'] == filter_op:
                return 'flt%d_%d' % (position, f['index'])


def possible_owners():
    return ContactModel.query.filter(
        ContactModel.isemployee == True).all()


class TelephoneModelView(EnhancedModelView):
    column_list = column_details_list = (
        'number', 'contact', 'company',)

    column_filters = (
        'number', 'contact', 'company',)
    column_searchable_list = ('number',)
    column_sortable_list = ('number',)


class EmailModelView(EnhancedModelView):
    form_rules = column_filters = column_list = column_details_list = (
        'email', 'contact', 'company', 'organization')
    column_searchable_list = ('email',)
    column_sortable_list = ('email', )


class FilterableMixin:
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        if self.mainfilter:
            filtered_objects = {}
            filtered_objects['emailsview'] = [
                EmailModelView(EmailModel, db.session), self.mainfilter]
            filtered_objects['telephonesview'] = [
                TelephoneModelView(TelephoneModel, db.session), self.mainfilter]
            filtered_objects['tasksview'] = [
                TaskModelView(TaskModel, db.session), self.mainfilter]
            filtered_objects['messagesview'] = [MessageModelView(
                MessageModel, db.session), self.mainfilter]
            filtered_objects['projectsview'] = [ProjectModelView(
                ProjectModel, db.session), self.mainfilter]
            filtered_objects['sprintsview'] = [SprintModelView(
                SprintModel, db.session), self.mainfilter]
            filtered_objects['dealsview'] = [DealModelView(
                DealModel, db.session), self.mainfilter]
            filtered_objects['commentsview'] = [CommentModelView(
                CommentModel, db.session), self.mainfilter]
            filtered_objects['linksview'] = [LinkModelView(
                LinkModel, db.session), self.mainfilter]

            self._template_args['filtered_objects'] = filtered_objects
        return super().edit_view()

    @expose('/details/', methods=('GET',))
    def details_view(self):
        if self.mainfilter:
            filtered_objects = {}
            filtered_objects['emailsview'] = [
                EmailModelView(EmailModel, db.session), self.mainfilter]
            filtered_objects['telephonesview'] = [
                TelephoneModelView(TelephoneModel, db.session), self.mainfilter]
            filtered_objects['tasksview'] = [
                TaskModelView(TaskModel, db.session), self.mainfilter]
            filtered_objects['messagesview'] = [MessageModelView(
                MessageModel, db.session), self.mainfilter]
            filtered_objects['projectsview'] = [ProjectModelView(
                ProjectModel, db.session), self.mainfilter]
            filtered_objects['sprintsview'] = [SprintModelView(
                SprintModel, db.session), self.mainfilter]
            filtered_objects['dealsview'] = [DealModelView(
                DealModel, db.session), self.mainfilter]
            filtered_objects['commentsview'] = [CommentModelView(
                CommentModel, db.session), self.mainfilter]
            filtered_objects['linksview'] = [LinkModelView(
                LinkModel, db.session), self.mainfilter]

            self._template_args['filtered_objects'] = filtered_objects
        return super().details_view()


class ContactModelView(FilterableMixin, EnhancedModelView):
    form_rules = column_details_list = ('firstname', 'lastname', 'description', 'emails', 'telephones', 'message_channels',
                                        'deals', 'comments', 'tasks', 'projects', 'messages', 'sprints', 'isemployee', 'links', 'owner', 'ownerbackup')
    form_edit_rules = ('firstname', 'lastname', 'description', 'emails', 'telephones', 'tasks', 'deals',
                       'message_channels', 'isemployee', 'owner', 'ownerbackup')

    column_filters = ('firstname', 'lastname', 'description', 'emails', 'telephones', 'message_channels',
                      'deals', 'comments', 'tasks', 'projects', 'messages', 'sprints', 'links', 'owner', 'ownerbackup')
    column_searchable_list = ('firstname', 'lastname',)
    column_list = ('id', 'firstname', 'lastname', 'emails',
                   'telephones', 'description')

    column_sortable_list = ('firstname', 'lastname')

    inline_models = [
        (TelephoneModel, {'form_columns': ['id', 'number']}),
        (EmailModel, {'form_columns': ['id', 'email']}),
        (TaskModel, {'form_columns': [
         'id', 'title', 'description', 'type', 'priority']}),
        (DealModel, {'form_columns': ['id', 'name', 'amount', 'currency', 'deal_type']})]

    form_args = {
        'isemployee': {'label': 'Employee?'},
        'owner': {'query_factory': possible_owners},
        'ownerbackup': {'query_factory': possible_owners, 'label': 'Backup Owner'},
    }

    mainfilter = "Contacts / Uid"


class CompanyModelView(FilterableMixin, EnhancedModelView):
    form_rules = column_filters = column_details_list = ('name', 'description', 'emails', 'telephones',
                                                         'deals', 'messages', 'tasks', 'comments', 'owner', 'ownerbackup')

    form_edit_rules = ('name', 'description', 'emails', 'telephones', 'messages', 'tasks', 'deals',
                       'owner', 'ownerbackup')

    column_searchable_list = ('id', 'name', 'description',)
    column_list = ('id', 'name', 'description', 'emails', 'telephones')
    column_sortable_list = ('name', )

    inline_models = [
        (TelephoneModel, {'form_columns': ['id', 'number']}), (EmailModel, {
            'form_columns': ['id', 'email']}),
        (TaskModel, {'form_columns': [
         'id', 'title', 'description', 'type', 'priority', ]}),
        (MessageModel, {'form_columns': ['id', 'title', 'channel']}),
        (DealModel, {'form_columns': ['id', 'name', 'amount', 'currency', 'deal_type', 'remarks', ]})]

    mainfilter = "Companies / Uid"


class OrganizationModelView(FilterableMixin, EnhancedModelView):
    form_rules = column_filters = column_details_list = ('name', 'description', 'emails',
                                                         'promoter', 'guardian', 'owner',
                                                         'sprints', 'tasks', 'users', 'messages', 'comments',
                                                         'links',)
    form_rules = ('name', 'description', 'emails',
                  'promoter', 'guardian', 'owner',)

    form_edit_rules = ('name', 'description', 'emails',
                       'promoter', 'guardian', 'owner', 'tasks', 'messages')
    column_list = ('id', 'name', 'emails', 'description', 'owner')
    column_searchable_list = ('id', 'name', 'description',)
    column_sortable_list = ('name',)

    inline_models = [
        (EmailModel, {
            'form_columns': ['id', 'email']}),
        (TaskModel, {'form_columns': [
         'id', 'title', 'type', 'priority', ]}),
        (MessageModel, {'form_columns': ['id', 'title', 'content', 'channel']})
    ]
    mainfilter = "Organizations / Uid"


class DealModelView(EnhancedModelView):
    column_filters = column_details_list = ('id', 'name',  'amount', 'currency', 'deal_type', 'deal_state',
                                            'contact', 'company' )

    form_rules = ('name',  'amount', 'currency', 'deal_type', 'deal_state',
                  'contact', 'company', 'owner', 'ownerbackup',
                  'remarks',)

    form_edit_rules = ('name',  'amount', 'currency', 'deal_type', 'deal_state',
                       'contact', 'company', 'owner', 'ownerbackup', 'tasks', 'messages')

    column_list = ('id', 'name', 'amount', 'currency','deal_type', 'deal_state')
    column_searchable_list = (
        'id', 'name', 'amount', 'currency', 'deal_type', 'deal_state')

    column_sortable_list = ('name', 'amount', 'currency',
                            'deal_type', 'deal_state')

    inline_models = [
        (TaskModel, {'form_columns': [
         'id', 'title', 'type', 'priority', ]}),
        (MessageModel, {'form_columns': ['id', 'title', 'content']})
    ]


class ProjectModelView(FilterableMixin, EnhancedModelView):
    column_filters = column_details_list = ('name', 'description', 'start_date', 'deadline',
                                            'promoter', 'sprint', 'tasks', 'guardian')
    form_rules = ('name', 'description', 'start_date', 'deadline',
                  'promoter', 'sprint', 'tasks', 'guardian',)

    edit_form_rules = ('name', 'description',
                       'start_date', 'deadline',
                       'promoter', 'guardian',
                       'users', 'tasks', 'messages')

    column_list = ('id', 'name', 'description', 'start_date', 'deadline', )
    column_searchable_list = (
        'id', 'name', 'description', 'start_date', 'deadline')
    column_sortable_list = ('name', 'start_date', 'deadline')

    inline_models = [
        (TaskModel, {'form_columns': [
         'id', 'title', 'description', 'type', 'priority', ]}),
        (MessageModel, {'form_columns': ['id', 'title', 'content', 'channel']})
    ]

    mainfilter = "Projects / Uid"


class SprintModelView(EnhancedModelView):
    column_filters = column_details_list = ('id', 'name', 'description', 'start_date', 'deadline',
                                            'promoter', 'guardian', 'parent', 'users',
                                            'comments', 'links', 'messages', )
    form_rules = ('name', 'description', 'start_date', 'deadline',
                  'promoter', 'guardian', 'parent',
                  )

    form_edit_rules = ('name', 'description', 'start_date', 'deadline',
                       'promoter', 'guardian', 'parent', 'users', 'tasks', 'messages')
    column_list = ('id', 'name', 'description', 'start_date', 'deadline')
    column_searchable_list = (
        'id', 'name', 'description', 'start_date', 'deadline')
    column_sortable_list = ('name', 'start_date', 'deadline')

    inline_models = [
        (TaskModel, {'form_columns': [
         'id', 'title', 'type', 'priority', ]}),
        (MessageModel, {'form_columns': ['id', 'title', 'content', 'channel']})
    ]

    mainfilter = "Sprints / Uid"


class CommentModelView(EnhancedModelView):
    column_filters = column_details_list = ('id', 'name', 'content',
                                            'company', 'contact', 'organization', 'project', 'sprint', 'task',
                                            'link', 'deal', 'sprint', 'remarks')
    form_rules = ('name', 'content',
                  'company', 'contact', 'organization', 'project', 'sprint', 'task',
                  'link', 'deal', 'sprint', 'remarks')
    form_edit_rules = ('name', 'content')
    column_list = ('id', 'name', 'content')
    column_searchable_list = ('id', 'name', 'content')
    column_sortable_list = ('name',)


class LinkModelView(EnhancedModelView):
    column_filters = column_details_list = ('url', 'contact', 'organization', 'task', 'project',
                                            'deal', 'sprint', 'labels', 'comments')
    form_rules = ('url', 'contact', 'organization', 'task', 'project',
                  'deal', 'sprint', 'labels',)
    form_edit_rules = ('url', 'labels')
    column_list = ('url', 'labels')
    column_searchable_list = ('id', 'url', 'labels')
    column_sortable_list = ('url', )


class TaskModelView(EnhancedModelView):
    column_details_list = ('id', 'title', 'description', 'content', 'contacts',
                           'type', 'priority', 'eta', 'time_done',
                           'company', 'organization', 'project', 'sprint', 'deal',
                           'comments', 'messages', 'remarks')

    column_filters = ('id', 'title', 'description', 'content', 'contacts',
                      'type', 'priority', 'eta', 'time_done',
                      'company', 'organization', 'project', 'sprint', 'deal',
                      'comments', 'messages', 'remarks')
    form_rules = ('title', 'description', 'content',
                  'type', 'priority', 'eta', 'time_done',
                  'contacts', 'company', 'organization', 'project', 'sprint', 'deal',
                  'remarks')

    form_edit_rules = ('title', 'description', 'content', 'remarks',
                       'type', 'priority', 'eta', 'time_done', 'comments',
                       'contacts', 'company', 'organization', 'project', 'sprint', 'deal',)
    column_list = ('id', 'title', 'description', 'contacts', 'eta', 'priority', 'time_done',
                   'organization', 'company', 'project', 'sprint', 'deal')
    column_searchable_list = ('id', 'title', 'description',
                              'content', 'type', 'priority', 'eta')
    column_sortable_list = ('eta', 'priority')

    inline_models = [
        (CommentModel, {'form_columns': [
         'id', 'name', 'content', 'remarks']}),
    ]   


class MessageModelView(EnhancedModelView):
    form_rules = column_filters  = ('id', 'title', 'content', 'channel', 'time_tosend', 'time_sent',
                                                         'company', 'contact', 'organization', 'project', 'sprint', 'deal', 'task')
    column_details_list = ('id', 'title', 'content','company', 'contact', 'organization', 'project', 'sprint', 'deal', 'task')

    form_edit_rules = ('title', 'content', 'channel',
                       'time_tosend', 'time_sent',)
    column_list = ('title', 'content',
                   'company', 'contact', 'deal', 'organizaton', 'task', 'project', 'sprint')
    column_searchable_list = ('title', 'content')
    column_sortable_list = ('title',)


class TaskAssignmentModelView(EnhancedModelView):
    column_details_list = ('contact', 'task', 'tasktracking')
    column_list = ('percent_completed', 'contact',
                   'task',)


class TaskTrackingModelView(EnhancedModelView):
    column_list = column_details_list = ('remarks',
                                         'time_done',)
