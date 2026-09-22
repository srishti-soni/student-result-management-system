import io
import pandas as pd


def generate_csv(df: pd.DataFrame) -> bytes:
    """Return UTF-8 CSV bytes for a DataFrame — suitable for st.download_button."""
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")
