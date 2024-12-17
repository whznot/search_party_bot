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
            current_media = profile.media.split(",") if profile.media else []
            if len(current_media) < 3:
                new_media = f"{media_type}:{media_file}"
                current_media.append(new_media)
                profile.media = ",".join(current_media)

    session.commit()
    return len(profile.media.split(",")) if profile.media else 0
