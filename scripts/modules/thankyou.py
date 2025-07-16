import streamlit as st

def show_thank_you_page():
    """Display the thank you page after successful registration"""
    st.balloons()

    st.markdown(
        """
        <div style="display: flex; justify-content: center;">
            <div style="max-width: 700px; text-align: center;">
                <h2>🎉 Welcome to She-for-STEM!</h2>
                <p style="font-size: 18px;">
                    Thanks for registering — you'll be enrolled soon.
                </p>
                <h3>👉 Start Learning:</h3>
                <p style="font-size: 17px;">
                    📱 <a href="https://play.google.com/store/apps/details?id=com.vigyanshaala.courses" target="_blank">Download App (Mobile)</a><br>
                    💻 <a href="https://mytribe.vigyanshaala.com/" target="_blank">Access on Computer</a><br>
                    🎥 <a href="https://bit.ly/VigyanShaala_App_Playlist" target="_blank">How to log in</a>
                </p>
                <h3>📢 WhatsApp Group Updates:</h3>
                <p style="font-size: 17px;">
                    You will be added to the WhatsApp group shortly. Stay tuned!
                </p>
                <p style="font-size: 18px;">
                    Excited to have you onboard!<br>
                    – Team VigyanShaala
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )