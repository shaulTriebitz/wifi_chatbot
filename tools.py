from langchain_core.tools import tool
from typing import Optional, Dict, Any, List
import requests
from bs4 import BeautifulSoup


@tool
def freq_to_channel(freq: float) -> Optional[int]:
    """
    Convert a given frequency (MHz) to its corresponding WiFi channel.
    
    Supports:
      - 2.4 GHz band:
          * Channels 1-13: center frequency = 2407 + 5 * channel.
          * Channel 14: center frequency = 2484 MHz.
      - 5 GHz band:
          * Center frequency = 5000 + 5 * channel.
      - 6 GHz band:
          * Center frequency = 5950 + 5 * channel.
            (For example, 5955 MHz corresponds to channel 1, 5975 MHz to channel 5, etc.)
    
    Parameters:
        freq (float): Frequency in MHz.
    
    Returns:
        Optional[int]: WiFi channel number if valid, otherwise None.
    """
    # 2.4 GHz band: channels 1-13 and channel 14
    if 2412 <= freq <= 2472:
        return int((freq - 2407) // 5)
    elif freq == 2484:
        return 14
    # 5 GHz band:
    elif 5180 <= freq <= 5825:
        if (freq - 5000) % 5 == 0:
            return int((freq - 5000) // 5)
        else:
            return None
    # 6 GHz band:
    elif 5955 <= freq <= 7115:
        if (freq - 5950) % 5 == 0:
            return int((freq - 5950) // 5)
        else:
            return None
    else:
        # Frequency not recognized as a standard WiFi channel
        return None


@tool
def channel_to_freq(channel: int, band: Optional[str] = None) -> Optional[float]:
    """
    Convert a WiFi channel to its corresponding frequency in MHz.
    
    Parameters:
        channel (int): WiFi channel number.
        band (Optional[str]): Frequency band as a string: "2.4", "5", or "6".
            If None, the function will assume:
              - 2.4 GHz if channel is between 1 and 14.
              - Otherwise, if band is not provided for channels >14, the conversion is ambiguous.
    
    Returns:
        Optional[float]: The center frequency in MHz if valid, otherwise None.
    
    Conversion formulas:
      - 2.4 GHz:
          * For channels 1-13: frequency = 2407 + 5 * channel
          * For channel 14: frequency = 2484 MHz
      - 5 GHz:
          * frequency = 5000 + 5 * channel
      - 6 GHz:
          * frequency = 5950 + 5 * channel
    """
    if band is None:
        # Assume 2.4 GHz for channel numbers 1 to 14.
        if 1 <= channel <= 14:
            band = "2.4"
        else:
            # Without a specified band, channels outside 1-14 are ambiguous.
            return None

    if band == "2.4":
        if 1 <= channel <= 13:
            return 2407 + 5 * channel
        elif channel == 14:
            return 2484
        else:
            return None
    elif band == "5":
        # For 5 GHz, we use a simple offset.
        return 5000 + 5 * channel
    elif band == "6":
        # For 6 GHz, the conversion is similar.
        return 5950 + 5 * channel
    else:
        # Unsupported band specified.
        return None


@tool
def get_wifi_channel_info() -> List[Dict[str, Any]]:
    """
    Gets general WiFi channel information from the fixed Wikipedia page:
    "https://en.wikipedia.org/wiki/List_of_WLAN_channels"
    
    The function extracts all tables with the class "wikitable" and returns each table as a dictionary containing:
      - "caption": The table caption (if available)
      - "headers": A list of header strings from the table
      - "rows": A list of dictionaries, each mapping header names to the cell contents of that row
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the scraped tables.
    """
    url = "https://en.wikipedia.org/wiki/List_of_WLAN_channels"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve the page: {url} (status code: {response.status_code})")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = []
    
    for table in soup.find_all("table", class_="wikitable"):
        table_data = {}
        # Get table caption if available
        caption_tag = table.find("caption")
        table_data["caption"] = caption_tag.get_text(strip=True) if caption_tag else None
        
        # Extract headers from the first row
        headers = []
        header_row = table.find("tr")
        if header_row:
            for th in header_row.find_all(["th", "td"]):
                header_text = th.get_text(strip=True)
                headers.append(header_text)
        table_data["headers"] = headers
        
        # Extract data rows (skip header row)
        rows = []
        for tr in table.find_all("tr")[1:]:
            cells = tr.find_all(["td", "th"])
            if not cells:
                continue
            row_data = {}
            for idx, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                key = headers[idx] if idx < len(headers) else f"column_{idx+1}"
                row_data[key] = cell_text
            rows.append(row_data)
        table_data["rows"] = rows
        
        tables.append(table_data)
    
    return tables


# Maps the function names to the actual function object in the script
# This mapping will also be used to create the list of wifi_tools to bind to the agent
wifi_tools = {
    "freq_to_channel": freq_to_channel,
    "channel_to_freq": channel_to_freq,
    "get_wifi_channel_info": get_wifi_channel_info,
}
