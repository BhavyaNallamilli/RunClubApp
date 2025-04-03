import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from running_club import app, db
from running_club.models import Profile
import os

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        os.makedirs(os.path.join('runclub', 'static', 'gallery', 'Runs'), exist_ok=True)
        os.makedirs(os.path.join('runclub', 'static', 'gallery', 'Events'), exist_ok=True)
        os.makedirs(os.path.join('runclub', 'static', 'gallery', 'Sports'), exist_ok=True)
        os.makedirs(os.path.join('runclub', 'static', 'profile_photos'), exist_ok=True)
        os.makedirs(os.path.join('runclub', 'static', 'qrcodes'), exist_ok=True)

        if not Profile.query.first():
            new_profile = Profile(name="Run Club Member", photo="placeholder.jpg", dob="YYYY-MM-DD", instagram="@runclub", bio="Join our running community!")
            db.session.add(new_profile)
        db.session.commit()
    app.run(debug=True)