from app.database import engine, SessionLocal
from app.models import Base, Chapter, FormTemplate, EduContent

def init():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Seeding Chapter Mahardika...")
        chapter = Chapter(
            name="Mahardika",
            city="Bandung",
            region="Jawa Barat",
            meeting_day="Wednesday",
            meeting_time="07:00"
        )
        db.add(chapter)
        db.commit()
        db.refresh(chapter)

        print("Seeding Default Form...")
        form = FormTemplate(
            chapter_id=chapter.id,
            name="Business Profile",
            slug="business-profile",
            description="Kenali bisnis member — 3 pertanyaan, 2 menit",
            form_type="business_profile",
            questions=[
                {
                    "key": "q1_products",
                    "label": "Produk/jasa yang paling laku dan paling mahal?",
                    "type": "textarea",
                    "required": True,
                    "hint": "Spesifik. Bukan 'building materials' tapi 'distributor besi beton untuk proyek konstruksi'"
                },
                {
                    "key": "q2_customers",
                    "label": "Customer ideal siapa? (Spesifik)",
                    "type": "textarea",
                    "required": True,
                    "hint": "Bukan 'semua orang' tapi 'owner restoran yang mau buka cabang ke-2'"
                },
                {
                    "key": "q3_partners",
                    "label": "Kalau dapat project, siapa di chapter yang pasti diajak?",
                    "type": "textarea",
                    "required": True,
                    "hint": "Tulis nama member + alasannya"
                }
            ],
            is_active=True
        )
        db.add(form)

        print("Seeding Default Edu...")
        edu = EduContent(
            chapter_id=chapter.id,
            title="Kenali Tetangga Bisnis Lo",
            slug="kenali-tetangga-bisnis",
            description="Edu moment tentang pentingnya mengenal detail bisnis sesama member",
            slides=[
                {"type": "title", "heading": "Kenali Tetangga Bisnis Lo", "subtext": "Edu Moment — Chapter Mahardika"},
                {"type": "text", "heading": "Bobby jual besi. Erick jual APAR.", "body": "Klasifikasi BNI sama: Building Materials. Tapi customer beda. Referral beda. Power Team harusnya beda."},
                {"type": "stat", "number": "20", "caption": "dari 51 member yang kita tahu detail bisnisnya"},
                {"type": "text", "heading": "Kalau gak kenal bisnis temen, referral nyasar.", "body": "Refer ke 'building material' padahal yang dibutuhin APAR, bukan besi."},
                {"type": "text", "heading": "3 pertanyaan. 2 menit.", "body": "1. Produk/jasa paling laku dan paling mahal?\n2. Customer ideal siapa — spesifik?\n3. Siapa di chapter yang pasti diajak kalau dapat project?"},
                {"type": "text", "heading": "Dari jawaban ini, sistem otomatis tahu:", "body": "Siapa serve market yang sama → Power Team\nSiapa yang belum ada tapi dibutuhkan → Top 10 Wanted\nSiapa customer terbesar chapter → Top Customers"},
                {"type": "cta", "heading": "Scan. Isi. Selesai.", "button_text": "Isi Sekarang", "button_url": "/form/business-profile"}
            ],
            is_published=True
        )
        db.add(edu)
        db.commit()
        print("Done!")
    finally:
        db.close()

if __name__ == "__main__":
    init()
