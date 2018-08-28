from pyggel import net2
from io import BytesIO


def main():

    formatters = {
        'text': net2.TextFormat,
        'json': net2.JsonFormat,
        'msg': net2.MsgpackFormat
    }

    for format in formatters:
        print('format:', format)
        pack = formatters[format]()
        buf = BytesIO()

        buf.write(pack.format('abc'))
        buf.write(pack.format('def'))
        buf.write(pack.format('ghi'))
        print('\tbuf:', buf.getvalue())

        recv = list(pack.unformat(buf.getvalue()))
        print('\trecv:', recv)

        # also test individual
        out = pack.format('test')
        print('\ttest?', list(pack.unformat(out)))

main()
