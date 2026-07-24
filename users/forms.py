from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'country', 'favourite_anime', 'profile_picture']
from django import forms
from .models import Group, GroupPost

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']

class GroupPostForm(forms.ModelForm):
    class Meta:
        model = GroupPost
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write something...'})
        }
from django import forms
from .models import FeatureFeedback

class FeatureFeedbackForm(forms.ModelForm):
    class Meta:
        model = FeatureFeedback
        fields = ['feature_request', 'likes_about_site']
        widgets = {
            'feature_request': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'What feature would you love to see added?'
            }),
            'likes_about_site': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'What do you like about the site so far?'
            }),
        }
