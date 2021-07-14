import sys

cmd = sys.argv[1] if len(sys.argv) > 1 else None

sys.argv = sys.argv[:1] + sys.argv[2:]

print(sys.argv)
if cmd == '--infer':
    from deploy.python import infer
    infer.main()
elif cmd == '--mot':
    from tools import infer_mot
    infer_mot.main()
else:
    print("Usage: <--infer|--mot> arguments...")
