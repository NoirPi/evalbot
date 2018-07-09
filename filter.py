from discord import Message, Member, TextChannel

allowed_languages = {
    365161457995743252: ['python3', 'python2'],
    365161096199536662: ['java'],
    365162262400598016: ['nodejs'],
    365162403526082561: ['php'],
    411245017764462593: ['java'],
    440476654767177728: ['java'],
    395547238165643265: ['csharp'],
    365161847529275393: ['cpp14'],
    440476086300573696: ['go'],
    440476142881996810: ['ruby'],
}

everything = [365162674033524746, 365236060252536833]


def verify(message: Message, language: str):
    if not message.guild:
        return False
    author: Member = message.author
    channel: TextChannel = message.channel
    if author.guild_permissions.manage_messages:
        return True

    if channel.id in everything:
        return True

    if language in allowed_languages.get(channel.id, []):
        return True

    return False
