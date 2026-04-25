import os

from jinja2 import BaseLoader, Environment, FileSystemLoader

# Template dir with check
template_dir = os.path.join(os.path.dirname(__file__), "../../templates")
if os.path.exists(template_dir):
    env = Environment(loader=FileSystemLoader(template_dir),
                      block_start_string="[%", block_end_string="%]")
else:
    env = Environment(loader=BaseLoader())  # Fallback empty
    print("Warning: templates not found, using fallback.")

    template = env.from_string("""
# Резюме для {{ job.title }}

**Имя:** {{ profile.name }}
**Навыки:** {{ profile.skills | join(', ') }}

## Опыт работы

{% for exp in profile.experience %}
- {{ exp.duration }}: {{ exp.position }} в {{ exp.company }}
  - {{ exp.description }}
{% endfor %}

## Проекты

{% for project in profile.projects %}
- {{ project.name }}: {{ project.description }}
{% endfor %}

""")

    resume_content = template.render(job=job, profile=profile)
    return resume_content


