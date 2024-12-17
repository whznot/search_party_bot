from db import SessionLocal, Profile

def update_user_profile(user_id: int, updates: dict, media_file: str = None, media_type: str = None) -> int:
    with SessionLocal() as session:
        profile = session.query(Profile).filter_by(user_id=user_id).first()

        if updates:
            session.query(Profile).filter_by(user_id=user_id).update(updates)

        if media_file and media_type:
            new_media = f"{media_type}:{media_file}"
            if profile.media:
                profile.media += f", {new_media}"
            else:
                profile.media = new_media

        session.commit()

        if profile and profile.media:
            return len(profile.media.split(","))
        return 0