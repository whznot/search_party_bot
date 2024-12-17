from db import SessionLocal, Profile


def update_user_profile(user_id: int, updates: dict, media_file: str = None, media_type: str = None) -> int:
    with SessionLocal() as session:
        profile = session.query(Profile).filter_by(user_id=user_id).first()

        if not profile:
            profile = Profile(user_id=user_id, media="")
            session.add(profile)

        if updates:
            for key, value in updates.items():
                setattr(profile, key, value)

        if media_file and media_type:
            new_media = f"{media_type}:{media_file}"
            if profile.media:
                media_list = profile.media.split(",")
                if len(media_list) >= 3:
                    return len(media_list)
                profile.media += f",{new_media}"
            else:
                profile.media = new_media

        session.commit()

        return len(profile.media.split(",")) if profile.media else 0
