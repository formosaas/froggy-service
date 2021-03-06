from django.utils import timezone
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils import formats
from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    ForeignKey,
    CASCADE,
    PositiveIntegerField,
)
from django_fsm import FSMField, transition
from ckeditor.fields import RichTextField
from apps.mails.models import SendGridMail, SendGridMailTemplate
from bs4 import BeautifulSoup


class State(object):
    """案件處理狀態"""
    DRAFT = 'draft'
    PUBLISHED = 'published'

    CHOICES = (
        (DRAFT, '尚未發布'),
        (PUBLISHED, '已發布'),
    )


class Arrange(Model):
    """案件處理
    * case: 案件
    * title: 處理標題
    * state: 處理狀態
    * content: 處理內容
    * arrange_time: 處理時間
    * publish_time: 發布時間
    * update_time: 上次更新時間
    """
    state = FSMField(default=State.DRAFT, verbose_name=_('Arrange State'), choices=State.CHOICES)
    case = ForeignKey('cases.Case', on_delete=CASCADE, related_name='arranges', verbose_name=_('Case'))
    title = CharField(max_length=120, verbose_name=_('Arrange Title'))
    content = RichTextField(verbose_name=_('Content'))
    arrange_time = DateTimeField(null=True, blank=True, verbose_name=_('Arrange Time'))
    publish_time = DateTimeField(null=True, blank=True, verbose_name=_('Arrange Publish Time'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated Time'))

    order = PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _('Arrange')
        verbose_name_plural = _('Arrange')
        ordering = ('-arrange_time',)

    def __str__(self):
        return f'{self.case.number}-{self.title}'

    def format_arrange_time(self, format_='SHORT_DATETIME_FORMAT'):
        return formats.date_format(self.arrange_time, format_)

    def html_content(self):
        return mark_safe(self.content)
    html_content.short_description = _('Content')
    html_content.allow_tags = True

    @property
    def published(self):
        return self.state in ['published']

    @property
    def email_content(self):
        """將圖片取代為連結"""
        soup = BeautifulSoup(self.content, features="html.parser")
        for img in soup.find_all('img'):
            link = img['src']
            alt = img['alt']
            a = soup.new_tag('a', href=link, style="color:red;")
            a.string = alt or '圖片連結'
            img.replaceWith(a)
        return str(soup)

    ########################################################
    # Transition Conditions
    # These must be defined prior to the actual transitions
    # to be referenced.

    def can_publish(self):
        return self.case.state != 'draft' and self.arrange_time is not None
    can_publish.hint = '案件為處理中且處理時間不為空才能發布'

    ########################################################
    # Workflow (state) Transitions

    def send(self):
        origin = self.case.first_history
        template = SendGridMailTemplate.objects.get(name='進度報告')
        data = {
            'number': self.case.number,
            'username': origin.username,
            'case_title': origin.title,
            'title': self.title,
            'datetime': self.format_arrange_time(),
            'content': self.email_content,
        }
        SendGridMail.objects.create(case=self.case, template=template, data=data)

    @transition(field=state, source=State.DRAFT, target=State.PUBLISHED, conditions=[can_publish],
                permission=lambda instance, user: user.has_perm('cases.change_arrange'),
                custom={'button_name': '發布'})
    def publish(self):
        self.send()
        self.publish_time = timezone.now()
