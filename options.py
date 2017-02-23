# Options for killms pipeline code

import ConfigParser
import os
import struct

def _get_terminal_size_linux():
    ''' From https://gist.github.com/jtriley/1108174 '''
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except:
            pass
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])

def getcpus():
    nodefile=os.getenv('PBS_NODEFILE')
    if nodefile:
        lines=len(open(nodefile).readlines())
        return lines
    else:
        import multiprocessing
        return multiprocessing.cpu_count()

option_list = ( ( 'machine', 'NCPU_DDF', int, getcpus(),
                  'Number of CPUS to use for DDF'),
                ( 'machine', 'NCPU_killms', int, getcpus(),
                  'Number of CPUS to use for KillMS' ),
                ( 'data', 'mslist', str, None,
                  'Initial measurement set list to use -- must be specified' ),
                ( 'data', 'full_mslist', str, None,
                  'Full-bandwidth measurement set to use for final step, if any' ),
                ( 'data', 'colname', str, 'CORRECTED_DATA', 'MS column to use' ),
                ( 'solutions', 'ndir', int, 60, 'Number of directions' ),
                ( 'solutions', 'NChanSols', int, 1, 'NChanSols for killMS' ),
                ( 'solutions', 'dt', float, 1., 'Time interval for killMS (minutes)' ),
                ( 'solutions', 'LambdaKF', float, 0.5, 'Kalman filter lambda for killMS' ),
                ( 'solutions', 'NIterKF', list, [1, 6, 6], 'Kalman filter iterations for killMS for the three self-cal steps' ),
                ( 'solutions', 'normalize', list, ['AbsAnt', 'AbsAnt', 'Abs'], 'How to normalize solutions for the three self-cal steps' ),
                ( 'image', 'imsize', int, 20000, 'Image size in pixels' ),
                ( 'image', 'cellsize', float, 1.5, 'Pixel size in arcsec' ),
                ( 'image', 'robust', float, -0.15, 'Imaging robustness' ),
                ( 'image', 'final_robust', float, -0.5, 'Final imaging robustness' ),
                ( 'image', 'psf_arcsec', float, None, 'Force restore with this PSF size in arcsec if set, otherwise use default' ),
                ( 'image', 'final_psf_arcsec', float, None, 'Final image restored with this PSF size in arcsec' ),
                ( 'image', 'low_psf_arcsec', float, None, 'Low-resolution restoring beam in arcsec' ),
                ( 'image', 'low_robust', float, -0.20, 'Low-resolution image robustness' ),
                ( 'image', 'low_cell', float, 4.5, 'Low-resolution image pixel size in arcsec' ),
                ( 'image', 'low_imsize', int, None, 'Low-resolution image size in pixels' ),
                ( 'image', 'do_decorr', bool, True, 'Use DDF\'s decorrelation mode' ),
                ( 'image', 'HMPsize', int, 10, 'Island size to use HMP initialization' ),
                ( 'masking', 'thresholds', list, [25,20,10,5],
                  'sigmas to use in (auto)masking for initial clean and 3 self-cals'),
                ( 'masking', 'tgss', str, None, 'Path to TGSS catalogue file' ),
                ( 'masking', 'tgss_radius', float, 8.0, 'TGSS mask radius in pixels' ), 
                ( 'masking', 'tgss_flux', float, 300, 'Use TGSS components with peak flux in catalogue units (mJy) above this value' ),
                ( 'masking', 'tgss_extended', bool, False, 'Make extended regions for non-pointlike TGSS sources' ),
                ( 'masking', 'tgss_pointlike', float, 30, 'TGSS source considered pointlike if below this size in arcsec' ),
                ( 'masking', 'region', str, None, 'ds9 region to merge with mask'),
                ( 'masking', 'extended_size', int, None,
                  'If generating a mask from the bootstrap low-res images, use islands larger than this size in pixels' ),
                ( 'masking', 'extended_rms', float, 3.0,
                  'Threshold value defining an island in the extended mask'), 
                ( 'control', 'quiet', bool, False, 'If True, do not log to screen' ),
                ( 'control', 'nobar', bool, False, 'If True, do not print progress bars' ),
                ( 'control', 'logging', str, 'logs', 'Name of directory to save logs to, or \'None\' for no logging' ),
                ( 'control', 'dryrun', bool, False, 'If True, don\'t run anything, just print what would be run' ),
                ( 'control', 'restart', bool, True, 'If True, skip steps that would re-generate existing files' ),
                ( 'control', 'cache_dir', str, None, 'Directory for ddf cache files -- default is working directory'),
                ( 'control', 'clearcache', bool, True, 'If True, clear all DDF cache before running' ),
                ( 'control', 'bootstrap', bool, False, 'If True, do bootstrap' ),
                ( 'bootstrap', 'bscell', float, 4.5, 'Bootstrap image cell size') ,
                ( 'bootstrap', 'bsimsize', int, 6000, 'Bootstrap image size' ) ,
                ( 'bootstrap', 'catalogues', list, None, 'File names of catalogues for doing bootstrap' ),
                ( 'bootstrap', 'groups', list, None, 'Group numbers for catalogues. At least one match must be found in each group. Optional -- if not present each catalogue is in a different group.' ), 
                ( 'bootstrap', 'frequencies', list, None, 'Frequencies for catalogues (Hz)' ), 
                ( 'bootstrap', 'names', list, None, 'Short names for catalogues' ), 
                ( 'bootstrap', 'radii', list, None, 'Crossmatch radii for catalogues (arcsec)' ) )

def options(filename):

    # option_list format is: section, name, type, default
    # names must be unique -- section names are not used in output dict

    odict = {}
    config=ConfigParser.SafeConfigParser()
    config.read(filename)
    cased={int: config.getint, float: config.getfloat, bool: config.getboolean, str: config.get, list: lambda x,y: eval(config.get(x,y))}
    for o in option_list:
        if len(o)==4:
            (section, name, otype, default)=o
        else:
            (section, name, otype, default,_)=o
        try:
            result=cased[otype](section,name)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            result=default
        odict[name]=result
    if odict['logging']=='None':
        odict['logging']=None
    return odict

def typename(s):
    return str(s).replace("type '","").replace("'","")

def print_options():
    import textwrap
    from auxcodes import bcolors
    # expected to be called if a config file is not specified. Print a
    # list of options
    width,height=_get_terminal_size_linux()
    sections=sorted(set(x[0] for x in option_list))
    klen=max([len(x[1]) for x in option_list])
    tlen=max([len(typename(x[2])) for x in option_list])
    fstring='%-'+str(klen)+'s = %-'+str(tlen)+'s (default %s)'
    indent=' '*(klen+3)
    for s in sections:
        print bcolors.OKBLUE+'\n[%s]' % s+bcolors.ENDC
        for o in option_list:
            if len(o)==4:
                (section, name, otype, default)=o
                doc=None
            elif len(o)==5:
                (section, name, otype, default, doc)=o
            else:
                print 'Oops!',o
                continue
            if section==s:
                
                print bcolors.BOLD+fstring % (name, typename(otype), str(default))+bcolors.ENDC
                if doc is not None:
                    print textwrap.fill(doc,width-1,initial_indent=indent,subsequent_indent=indent)

if __name__=='__main__':
    
    #print options('example.cfg')
    print_options()
