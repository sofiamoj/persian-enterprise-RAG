from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from rag import ingest
from rag.models import Document


class Command(BaseCommand):
    help = "Index every file in sample_docs/ that is not indexed yet."

    def handle(self, *args, **options):
        folder = Path(settings.BASE_DIR) / "sample_docs"
        for path in sorted(folder.iterdir()):
            if path.suffix.lower() not in ingest.SUPPORTED or Document.objects.filter(name=path.name).exists():
                continue
            with path.open("rb") as f:
                ingest.ingest(path.name, f)
            self.stdout.write(f"Indexed {path.name}")
