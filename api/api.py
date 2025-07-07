from flask import Flask, request, jsonify
from tv_channels import ALL_CHANNELS, extract_video_url

app = Flask(__name__)


@app.route('/get-channel-video-url', methods=['POST'])
def get_channel():
    data = request.get_json()
    
    channel_type = data.get('channel_type')
    channel_name = data.get('channel_name')
    
    if channel_type in ALL_CHANNELS and channel_name in ALL_CHANNELS[channel_type]:
        found_channel = ALL_CHANNELS[channel_type][channel_name]
        url = extract_video_url(ALL_CHANNELS[channel_type][channel_name]["url"])
        # url_hd = extract_video_url(ALL_CHANNELS[channel_type][channel_name]["url_hd"])

        return jsonify({
            "success": True,
            "url": url
        })
    else:
        return jsonify({
            "success": False,
            "error": "Channel not found"
        })
@app.route('/get-all-channels', methods=['GET'])
def get_all_channels():
    
    return jsonify({
            "success": True,
            "channels": ALL_CHANNELS
        })


if __name__ == '__main__':
    app.run(debug=True)