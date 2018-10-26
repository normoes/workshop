from rest_framework import serializers


def node_url_restriction(node_url):
    """Validate the node url.
    """

    if len(node_url) == 0:
        raise serializers.ValidationError("Too short.")
    return node_url


class InfoPostSerializer(serializers.Serializer):
    """Serializes node url posted by user.
    """

    node_url = serializers.CharField(
        validators=[node_url_restriction]
    )
