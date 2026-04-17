from django.db import models

class StaticPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="Used in URLs and to identify the page (e.g., 'about', 'faq')")
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Support Page"
        verbose_name_plural = "Support Pages"
