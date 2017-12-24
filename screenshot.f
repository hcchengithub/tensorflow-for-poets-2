
    \ Usage:
    \    1. open DOSBox, cd to 剪刀, 石頭, 布 respectively to do followings
    \    2. make sure ffmpeg in path 
    \    3. ~\ailab\{classname}>python -m peforth include screenshot.f

    <py>  # Nonsense
    [
        #"135137scissors171224.mp4",
        #"135214scissors171224.mp4",
        #"135257scissors171224.mp4",
        "135339rock171224.mp4",
        "135411rock171224.mp4",
        "135552rock171224.mp4",
    ]
    </pyV> constant files // ( -- list ) filenames
    
    \ js> (15-0.1)*7 int tib. ==> 104 where n = 15
    \ Get video duration(length) 
    \ ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4

    import subprocess constant subprocess
    py: setattr(sys.modules['peforth'].projectk,'subprocess',v('subprocess'))
    
    0.1 constant (開頭一小段不要)  // ( -- f ) 單位: 秒
    7   constant (每秒抓幾張) // ( -- n ) 

    : (擷取時間點) // ( i -- f ) 傳回第 i 個點的擷取時間 f 
        1 (每秒抓幾張) / ( i delta ) * ( 從 0 開始算的點位 )
        (開頭一小段不要) + ; 


    s" ffmpeg -accurate_seek -ss " 
    s" {0:f} -i {1} -frames:v 1 " +
    s" {2}_{0:06.2f}.jpg" + 
    constant commandLine // ( -- "command line with {} slots" ) 
                         /// {0} is (擷取時間點), {1} is .mp4 filename, {2} is leading 8 of {1}
                         
    code mediaDuration # get given media file's duration
        child = subprocess.Popen(
            "ffprobe" +
            " -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 " +
            pop(),
            stdout = subprocess.PIPE, 
            stderr = subprocess.STDOUT
            )
        out, err = child.communicate()
        errcode = child.returncode
        # push({"stdout":out,"stderr":err,"errorlevel":errcode})
        if not errcode:
            push(float(out))
        else:
            push(0) # something wrong
        end-code 
        // ( pathname -- float ) Get video/audio file's duration by the ffprobe tool from ffmpeg
                         
    <py>                         
    for fn in v('files'):
        push(fn); vm.execute("mediaDuration"); duration = pop()
        len = (duration-v('(開頭一小段不要)'))*v('(每秒抓幾張)')
        for i in range(int(len)): 
            push(i) 
            vm.dictate('(擷取時間點)')
            cmd = v('commandLine').format(pop(),fn,(fn+'_'*8)[:9])
            vm.dictate('dos %s' % cmd)
    </py>

    