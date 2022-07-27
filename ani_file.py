from chunk import Chunk
import builtins
import struct

class ani_read:
    def initfp(self, file):
        self._file = Chunk(file, bigendian = 0)

        #Check if file is an .ani file
        if self._file.getname() != b"RIFF":
            raise Exception("file does not start with RIFF id")
        if self._file.read(4) != b"ACON":
            raise Exception("not an .ANI file")

        #Checks for proper .ani file
        self._has_anih_chunk = False


        #loop through each chunk
        while 1:
            try:
                chunk = Chunk(self._file, bigendian = 0)
            except EOFError:
                break

            chunkname = chunk.getname()
            print(chunkname)

            if chunkname == b'anih':
                self._read_anih_chunk(chunk)
                self._has_anih_chunk = True
            #Got 2 kinds of LIST chunks: 'INFO' or 'fram'
            elif chunkname == b"LIST":
                listname = chunk.read(4)
                print(listname)
                if listname == b"INFO":
                    self._read_info_chunk(chunk)
                elif listname == b"fram":
                    self._frames = self._read_fram_chunk(chunk)
            elif chunkname == b"seq ":
                self._read_seq_chunk(chunk)
            chunk.skip()
            
        #Check for proper .ani file
        if not self._has_anih_chunk:
            raise Exception("anih chunk and/or fram chunk missing")

    def __init__(self, file):
        self._i_opened_the_file = None
        if isinstance(file, str):
            file = builtins.open(file, 'rb')
            self._i_opened_the_file = file
        # else, assume it is an open file object already
        try:
            self.initfp(file)
        except:
            if self._i_opened_the_file:
                file.close()
            raise
    
    #TODO: Not sure if these 3 are really needed. Might want to brush up on python class
    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    #
    # User visible method
    #
    def getfp(self):
        return self._file

    def close(self):
        self._file = None
        file = self._i_opened_the_file
        if file:
            self._i_opened_the_file = None
            file.close()

    def getnframes(self):
        return self._nFrames

    #TODO: NOT TESTED DUE TO NOT HAVING ANY .ANI FILE WITH THE DATA
    def getauthor(self):
        return self._iart or "no author data is included in the file"

    #TODO: NOT TESTED DUE TO NOT HAVING ANY .ANI FILE WITH THE DATA
    def getname(self):
        return self._inam or "no name is included in the file"

    def getseq(self):
        return self._seq
        
    def getframedata(self):
        return self._frames

    def getframestofile(self, outputpath=".\\", filenameprefix=""):
        frames = self._frames

        for id, frame in enumerate(frames):
            path = outputpath+"\\"+filenameprefix+str(id)+".ico"
            new_frame = builtins.open(path, "wb")
            new_frame.write(frame)
            new_frame.close()


    #
    # Internal methods
    #

    def _read_anih_chunk(self, chunk):
        try:
            cbSize, self._nFrames, self._nSteps, self._iWidth, self._iHeight, self._iBitCount, self._nPlanes, self._iDispRate, self._bfAttributes = struct.unpack_from("<9I", chunk.read(36))
            print(cbSize, self._nFrames, self._nSteps, self._iWidth, self._iHeight, self._iBitCount, self._nPlanes, self._iDispRate, self._bfAttributes)
        #TODO: look into what this except actually means
        except struct.error:
            raise EOFError from None

        #TODO: might want to put some checks

    #TODO: THIS HAS NOT BEEN TESTED SINCE I DONT HAVE ANY .ANI FILE WITH INFO CHUNK
    def _read_info_chunk(self, chunk):
        while 1:
            try:
                chunk = Chunk(chunk, bigendian=0)
            except EOFError:
                break

            if chunk.chunkname() == b"INAM":
                self._inam = chunk.read(chunk.getsize()).decode("utf-8")
            elif chunk.chunkname() == b"IART":
                self._iart = chunk.read(chunk.getsize()).decode("utf-8")
    
    def _read_fram_chunk(self, chunk):
        #TODO: support bitmaps frames
        if (self._bfAttributes!=3 and self._bfAttributes!=1):
            raise Exception("Frame info is in bitmaps (instead of ico) which is not supported for now")
            
        frames = list()

        while 1:
            try:
                frame_chunk = Chunk(chunk, bigendian = 0)
            except EOFError:
                break

            frames.append(frame_chunk.read(frame_chunk.getsize()))
            frame_chunk.skip()
        return frames

    def _read_seq_chunk(self, chunk):
        self._seq = tuple()
        for i in range(self._nSteps):
            self._seq += struct.unpack_from("I", chunk.read(4))

class ani_write:
    pass

def open(file, mode=None):
    if mode is None:
        if hasattr(file, "mode"):
            mode = file.mode
        else:
            mode = "rb"
    if mode in ("r", "rb"):
        return ani_read(file)
    elif mode in ("w", "wb"):
        return ani_write(file)
    else:
        raise Exception("Mode must be 'r', 'rb', 'w', or 'wb'")

